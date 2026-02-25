import asyncio
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from .schemas import ChatRequest, ChatResponse, Citation
from .dependencies import get_chat_engine

router = APIRouter()

from sqlalchemy.orm import Session
from .database import get_db
from .models import ChatSession, ChatMessage

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, engine=Depends(get_chat_engine), db: Session = Depends(get_db)):
    """
    Endpoint principal para conversar com o Agente via RAG local.
    Pode retornar tanto um JSON blocante quanto um Event-Stream (SSE) para digitação em tempo real.
    """
    
    # Gerenciamento de Sessão: Criar ou Reaproveitar
    if request.session_id:
        session_obj = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session_obj:
            session_obj = ChatSession(title=request.message[:50])
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)
    else:
        session_obj = ChatSession(title=request.message[:50] + "...")
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        
    # Grava a mensagem do Usuário no DB
    user_msg_db = ChatMessage(session_id=session_obj.id, role="user", content=request.message)
    db.add(user_msg_db)
    db.commit()

    if request.stream:
        async def event_generator():
            # Injetar o documento ativo como memória do sistema (apenas se existir) para não sujar a busca BM25/Vector
            temp_sys_msg = None
            if request.active_document:
                from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                temp_sys_msg = LlamaMsg(role=MessageRole.USER, content=f"Aqui está o texto do meu documento ativo no Obsidian, APENAS CONSIDERE ele caso minha próxima pergunta tenha a ver com ele. NÃO invente informações se eu não perguntar:\n{request.active_document}")
                engine._memory.put(temp_sys_msg)

            try:
                # Executar query_engine via thread para não bloquear o Async Loop do ASGI
                response = await asyncio.to_thread(engine.stream_chat, request.message)
                
                full_ai_response = ""
                
                if isinstance(response, str) or not hasattr(response, 'response_gen'):
                    full_ai_response = str(response)
                    yield f"data: {json.dumps({'content': full_ai_response, 'session_id': session_obj.id})}\n\n"
                else:
                    for token in response.response_gen:
                        full_ai_response += token
                        # Enviando tokens em formato padrão SSE
                        yield f"data: {json.dumps({'content': token})}\n\n"
                    
                    # Heurística abrangente para ocultar fontes em respostas triviais/conversacionais
                    texto = full_ai_response.lower()
                    
                    # Sinais de que a IA não tirou a resposta da documentação
                    is_denial = any(phrase in texto for phrase in [
                        "não encontrei", "não há informações", "não tenho acesso", 
                        "não há menção", "nenhuma menção", "não menciona", 
                        "como assistente", "posso estar errado", "não possuo acesso",
                        "não consigo", "desculpe", "fora do contexto"
                    ])
                    
                    # Sinais de que é apenas conversa ou resposta curta
                    is_trivial_chit_chat = len(texto) < 400 and not any(word in texto for word in [
                        "contexto", "documento", "arquivo", "pasta", "projeto", "código", "relatório", "anotação"
                    ])
                    
                    if not (is_denial or is_trivial_chit_chat):
                        # Extrair Fontes no Final
                        source_nodes = getattr(response, "source_nodes", [])
                        sources = set()
                        if source_nodes:
                            for node_w_score in source_nodes:
                                metadata = node_w_score.node.metadata
                                if not metadata:
                                    continue
                                    
                                if "file_path" in metadata:
                                    sources.add(f"📄 {metadata['file_path']}")
                                elif "file_name" in metadata:
                                    sources.add(f"📄 {metadata['file_name']}")
                                    
                            if sources:
                                sources_str = "\n".join(sources)
                                final_msg = f"\n\n**Fontes:**\n{sources_str}"
                                full_ai_response += final_msg
                                yield f"data: {json.dumps({'content': final_msg})}\n\n"
                                
                # Gravar a mensagem da IA no banco de dados AO FINAL do streaming
                ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response)
                db.add(ai_msg_db)
                db.commit()
                
                # Signal the frontend containing the session_id so it can anchor the thread
                yield f"data: {json.dumps({'session_id_established': session_obj.id})}\n\n"
            finally:
                # Limpar o documento ativo da memória apenas APÓS o stream de resposta para não cortar o raciocínio da IA
                if temp_sys_msg:
                    try:
                        all_history = engine._memory.get_all()
                        # Apenas remove a mensagem temporária baseada na role e no conteúdo para manter o buffer limpo
                        clean_history = [m for m in all_history if m.content != temp_sys_msg.content]
                        engine._memory.chat_store.set_messages(engine._memory.chat_store_key, clean_history)
                    except Exception as e:
                        print(f"[Warning] Failed to cleanup temp document memory: {e}")
                        
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
        sources = set()
        if not (is_denial or is_trivial_chit_chat):
            source_nodes = getattr(response, "source_nodes", [])
            if source_nodes:
                for node_w_score in source_nodes:
                    metadata = node_w_score.node.metadata
                    if not metadata:
                        continue
                    if "file_path" in metadata:
                        sources.add(f"📄 {metadata['file_path']}")
                    elif "file_name" in metadata:
                        sources.add(f"📄 {metadata['file_name']}")
                    
        return ChatResponse(
            response=str(response),
            sources=[Citation(source=s) for s in sorted(sources)]
        )
