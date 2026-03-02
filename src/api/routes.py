import asyncio
import json
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from .schemas import ChatRequest, ChatResponse, Citation, SettingsRequest, SettingsResponse, SessionUpdateRequest, UploadResponse, DocumentUpdateRequest
from .dependencies import get_chat_engine

router = APIRouter()

from sqlalchemy.orm import Session  # noqa: E402
from .database import get_db  # noqa: E402
from .models import ChatSession, ChatMessage, SystemSettings, SensusDocumentModel  # noqa: E402
from .auth import get_current_user  # noqa: E402

# Importando o limiter configurado no main.py
try:
    from .main import limiter
except ImportError:
    # Fallback seguro para testes unitários isolados
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)

@router.post("/chat")
@limiter.limit("15/minute")
async def chat_endpoint(request: Request, body_request: ChatRequest, engine=Depends(get_chat_engine), db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Endpoint principal para conversar com o Agente via RAG local.
    Pode retornar tanto um JSON blocante quanto um Event-Stream (SSE) para digitação em tempo real.
    """
    
    # Gerenciamento de Sessão: Criar ou Reaproveitar
    if body_request.session_id:
        session_obj = db.query(ChatSession).filter(ChatSession.id == body_request.session_id, ChatSession.tenant_id == tenant_id).first()
        if not session_obj:
            session_obj = ChatSession(title=body_request.message[:50], tenant_id=tenant_id)
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)
    else:
        session_obj = ChatSession(title=body_request.message[:50] + "...", tenant_id=tenant_id)
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        
    # Grava a mensagem do Usuário no DB
    user_msg_db = ChatMessage(session_id=session_obj.id, role="user", content=body_request.message, tenant_id=tenant_id)
    db.add(user_msg_db)
    db.commit()

    if body_request.stream:
        async def event_generator():
            # Injetar o documento ativo como memória do sistema (apenas se existir) para não sujar a busca BM25/Vector
            temp_sys_msg = None
            if body_request.active_document:
                from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                temp_sys_msg = LlamaMsg(role=MessageRole.USER, content=f"Aqui está o texto do meu documento ativo no Obsidian, APENAS CONSIDERE ele caso minha próxima pergunta tenha a ver com ele. NÃO invente informações se eu não perguntar:\n{body_request.active_document}")
                engine._memory.put(temp_sys_msg)

            try:
                # Interceptar comando remoto /web
                is_web_query = body_request.message.strip().startswith('/web')
                response = None
                
                if is_web_query:
                    import re
                    from src.web_search import search_web
                    from src.engine_builder import resolve_dynamic_llm
                    from src.config import llm as default_llm
                    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                    
                    from datetime import datetime
                    
                    web_args = body_request.message.strip()[4:].strip()
                    timelimit = None
                    match = re.match(r'^(-[dwmy])\s+(.*)', web_args)
                    if match:
                        timelimit = match.group(1)[1]  # 'd', 'w', 'm', 'y'
                        web_query = match.group(2).strip()
                    else:
                        web_query = web_args
                    
                    if web_query:
                        time_labels = {'d': 'últimas 24h', 'w': 'última semana', 'm': 'último mês', 'y': 'último ano'}
                        time_info = f" ({time_labels.get(timelimit, '')})" if timelimit else ""
                        yield f"data: {json.dumps({'content': f'🌐 *Buscando na web...{time_info}*\n\n'})}\n\n"
                        
                        # run search_web in thread so async loop isn't blocked
                        web_result = await asyncio.to_thread(search_web, web_query, timelimit)
                        
                        current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        sys_prompt = f"""Você é um assistente RAG de Pesquisa Web super avançado.
A data e hora atuais do sistema são: {current_date}

EXTREMA IMPORTÂNCIA:
1. Responda à pergunta do usuário baseando-se ÚNICA E EXCLUSIVAMENTE nos "Resultados Web (DuckDuckGo)" fornecidos na última mensagem.
2. NUNCA mencione que você é uma IA, ou que seu conhecimento foi cortado. NUNCA peça desculpas. Aja com extrema confiança e seja direto.
3. Se os resultados listarem a data de hoje, use isso como a verdade absoluta.
4. IMPORTANTE: Você recebeu "Extrações Profundas da Página" contendo o texto cru dos sites. Se houver dados tabulares, de times ou classificações no texto, construa uma bela Tabela Markdown (com | colunas |) para apresentar os dados ao usuário!
5. Formate a resposta de forma polida e direta, citando os links originais sempre que pertinente."""
                        
                        sys_msg = LlamaMsg(role=MessageRole.SYSTEM, content=sys_prompt)
                        context_msg = LlamaMsg(role=MessageRole.USER, content=f"Resultados Web (DuckDuckGo):\n{web_result}\n\nPergunta do usuário baseada na pesquisa web: {body_request.message}")
                        
                        # Injetar Histórico Base para a IA se lembrar do contexto da conversa
                        history_msgs = engine._memory.get_all() if engine else []
                        messages_to_send = [sys_msg] + history_msgs + [context_msg]
                        
                        active_llm = resolve_dynamic_llm(body_request.provider, body_request.model, default_llm)
                        response_gen = await active_llm.astream_chat(messages_to_send)
                        
                        full_ai_response = f"🌐 *Buscando na web...{time_info}*\n\n"
                        async for token in response_gen:
                            if token.delta:
                                full_ai_response += token.delta
                                yield f"data: {json.dumps({'content': token.delta})}\n\n"
                    else:
                        full_ai_response = "⚠️  **Uso:** `/web <query>`\n\n**Filtros:** `/web -d` (dia), `/web -w` (semana), `/web -m` (mês), `/web -y` (ano)"
                        yield f"data: {json.dumps({'content': full_ai_response})}\n\n"

                elif body_request.message.strip().startswith('/sys'):
                    from src.engine_builder import build_system_chat_engine
                    import logging
                    logger_routes = logging.getLogger(__name__)
                    sys_query = body_request.message.strip()[4:].strip()
                    
                    if not sys_query:
                        full_ai_response = "⚠️  **Uso:** `/sys <pergunta sobre a arquitetura do backend>`"
                        yield f"data: {json.dumps({'content': full_ai_response})}\n\n"
                    else:
                        yield f"data: {json.dumps({'content': '🧠 *Consultando Sistema Meta-RAG...*\n\n'})}\n\n"
                        try:
                            sys_engine = build_system_chat_engine(body_request.provider, body_request.model)
                            if not sys_engine:
                                full_ai_response = "❌ Erro: O Motor de Sistema não pôde ser iniciado. O banco vetorial foi criado?"
                                yield f"data: {json.dumps({'content': full_ai_response})}\n\n"
                            else:
                                response = await sys_engine.astream_chat(sys_query)
                                full_ai_response = "🧠 *Consultando Sistema Meta-RAG...*\n\n"
                                
                                async_gen = response.async_response_gen()
                                async for token in async_gen:
                                    full_ai_response += token
                                    yield f"data: {json.dumps({'content': token})}\n\n"
                                    
                                # Adiciona a trilha de auditoria dos arquivos analisados pela IA
                                source_nodes = getattr(response, "source_nodes", [])
                                sources = set()
                                for node_w_score in source_nodes:
                                    metadata = node_w_score.node.metadata
                                    if metadata and metadata.get("file_path"):
                                        import os
                                        filename = os.path.basename(metadata.get('file_path'))
                                        sources.add(f"🛠️ {filename}")
                                        
                                if sources:
                                    sources_str = "\n".join(sources)
                                    final_msg = f"\n\n**Arquivos Analisados:**\n{sources_str}"
                                    full_ai_response += final_msg
                                    yield f"data: {json.dumps({'content': final_msg})}\n\n"
                        except Exception as e:
                            logger_routes.error(f"Meta-RAG Error: {e}")
                            full_ai_response = f'❌ Erro interno no Meta-RAG: {e}'
                            yield f"data: {json.dumps({'content': full_ai_response})}\n\n"

                else:
                    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                    import asyncio
                    
                    # 1. Recuperar contexto do banco vetorial via Async
                    try:
                        source_nodes = await engine._retriever.aretrieve(body_request.message)
                    except Exception:
                        source_nodes = await asyncio.to_thread(engine._retriever.retrieve, body_request.message)
                        
                    # 2. Formatar o contexto
                    context_str = "\n\n".join([f"Documento (Path: {n.node.metadata.get('file_path', 'N/A')}):\n{n.node.get_content()}" for n in source_nodes]) if source_nodes else "Nenhum documento vetorial encontrado."
                    
                    # --- NEW: Phase 16.5 - The Semantic Router (Nurse Triage) ---
                    from src.core.the_nurse import TheNurse
                    nurse = TheNurse(body_request.provider, body_request.model)
                    intent_data = await nurse.evaluate_intent(body_request.message)
                    
                    if not intent_data.get("requires_doctor", True):
                        # Execução Tática Ultra-Rápida pela "Enfermeira"
                        response_gen = await nurse.execute_tactical_task(body_request.message, context_str, intent_data)
                        
                        full_ai_response = f"*(✨ Tarefa Tática Executada pela The Nurse ({intent_data.get('task_type', 'extraction')}))*\n\n"
                        yield f"data: {json.dumps({'content': full_ai_response})}\n\n"
                        
                        async for token in response_gen:
                            if token:
                                full_ai_response += token
                                yield f"data: {json.dumps({'content': token})}\n\n"
                    else:
                        # --- EXECUÇÃO TIER 4: O Médico (Heavy LLM & Deep Synthesis) ---
                        from src.core.the_doctor import TheDoctor
                        doctor = TheDoctor(body_request.provider, body_request.model, engine)
                        
                        yield f"data: {json.dumps({'content': '*(🧠 Raciocínio Profundo do The Doctor ativado...)*\\n\\n'})}\n\n"
                        
                        print(f"[DEBUG RAG] Executando The Doctor (Tier 4) via {getattr(doctor.llm, 'model', 'N/A')}...", flush=True)
                        response_gen = await doctor.execute_deep_reasoning(body_request.message, context_str, intent_data)
                        
                        full_ai_response = "*(🧠 Raciocínio Profundo do The Doctor ativado...)*\n\n"
                        async for token in response_gen:
                            if token:
                                full_ai_response += token
                                yield f"data: {json.dumps({'content': token})}\n\n"
                        
                # Após o streaming, verifique se a resposta foi apenas um aviso de que não achou o documento.
                if full_ai_response:
                    texto = full_ai_response.lower()
                    is_denial = any(word in texto for word in [
                        "não sei", "não tenho", "não encontrei", "não consigo", "desculpe", "fora do contexto", "não menciona", "não há informações", "não possui informações"
                    ])
                    
                    is_trivial_chit_chat = len(texto) < 400 and not any(word in texto for word in [
                        "contexto", "documento", "arquivo", "anotação", "base", "projeto", "código", "relatório", "anexo"
                    ])
                    
                    if not (is_denial or is_trivial_chit_chat):
                        # Usa a variável source_nodes alimentada manualmente no bloco normal, ou mocka se for /web!
                        s_nodes = locals().get('source_nodes', [])
                        sources = set()
                        for node_w_score in s_nodes:
                            metadata = node_w_score.node.metadata
                            if metadata:
                                file_path = metadata.get("file_path") or metadata.get("file_name") or ""
                                nome_base = str(file_path).replace('.md', '').replace('.txt', '').split('/')[-1].lower()
                                if nome_base and nome_base in texto:
                                    sources.add(f"📄 {file_path}")
                                    
                        if sources:
                            sources_str = "\n".join(sources)
                            final_msg = f"\n\n**Fontes:**\n{sources_str}"
                            full_ai_response += final_msg
                            yield f"data: {json.dumps({'content': final_msg})}\n\n"
                                
                # Gravar a mensagem da IA no banco de dados AO FINAL do streaming
                ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response, tenant_id=tenant_id)
                db.add(ai_msg_db)
                db.commit()
                db.refresh(ai_msg_db)
                
                # Signal the frontend containing the session_id so it can anchor the thread
                yield f"data: {json.dumps({'session_id_established': session_obj.id, 'message_id': ai_msg_db.id})}\n\n"
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
        
    else:
        # Lógica para resposta sem streaming (síncrona)
        is_web_query = body_request.message.strip().startswith('/web')
        is_sys_query = body_request.message.strip().startswith('/sys')
        
        if is_web_query:
            import re
            from src.web_search import search_web
            from src.engine_builder import resolve_dynamic_llm
            from src.config import llm as default_llm
            from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
            
            from datetime import datetime
            
            web_args = body_request.message.strip()[4:].strip()
            timelimit = None
            match = re.match(r'^(-[dwmy])\s+(.*)', web_args)
            if match:
                timelimit = match.group(1)[1]  # 'd', 'w', 'm', 'y'
                web_query = match.group(2).strip()
            else:
                web_query = web_args
            
            if web_query:
                time_labels = {'d': 'últimas 24h', 'w': 'última semana', 'm': 'último mês', 'y': 'último ano'}
                time_info = f" ({time_labels.get(timelimit, '')})" if timelimit else ""
                
                # run search_web in thread so async loop isn't blocked
                web_result = await asyncio.to_thread(search_web, web_query, timelimit)
                
                current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                sys_prompt = f"""Você é um assistente RAG de Pesquisa Web super avançado.
A data e hora atuais do sistema são: {current_date}

EXTREMA IMPORTÂNCIA:
1. Responda à pergunta do usuário baseando-se ÚNICA E EXCLUSIVAMENTE nos "Resultados Web (DuckDuckGo)" fornecidos na última mensagem.
2. NUNCA mencione que você é uma IA, ou que seu conhecimento foi cortado. NUNCA peça desculpas. Aja com extrema confiança e seja direto.
3. Se os resultados listarem a data de hoje, use isso como a verdade absoluta.
4. IMPORTANTE: Você NÃO tem capacidade de abrir links, clicar ou navegar nos sites. Você APENAS lê os trechos de texto fornecidos à você na pesquisa. Se o usuário pedir para "ler o link", extraia os dados APENAS dos trechos fornecidos ou explique que não pode navegar.
5. Formate a resposta de forma polida e direta, citando os links originais sempre que pertinente."""
                
                sys_msg = LlamaMsg(role=MessageRole.SYSTEM, content=sys_prompt)
                context_msg = LlamaMsg(role=MessageRole.USER, content=f"Resultados Web (DuckDuckGo):\n{web_result}\n\nPergunta do usuário baseada na pesquisa web: {body_request.message}")
                
                # Injetar Histórico Base para a IA se lembrar do contexto da conversa
                history_msgs = engine._memory.get_all() if engine else []
                messages_to_send = [sys_msg] + history_msgs + [context_msg]
                
                active_llm = resolve_dynamic_llm(body_request.provider, body_request.model, default_llm)
                response = await active_llm.achat(messages_to_send)
                
                full_ai_response = f"🌐 *Buscando na web...{time_info}*\n\n{str(response)}"
            else:
                full_ai_response = "⚠️  **Uso:** `/web <query>`\n\n**Filtros:** `/web -d` (dia), `/web -w` (semana), `/web -m` (mês), `/web -y` (ano)"
                
            # Gravar a mensagem da IA sincrona no SQLite
            ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response, tenant_id=tenant_id)
            db.add(ai_msg_db)
            db.commit()
            
            return ChatResponse(response=full_ai_response, sources=[])
            
        elif is_sys_query:
            from src.engine_builder import build_system_chat_engine
            import logging
            logger_routes = logging.getLogger(__name__)
            sys_query = request.message.strip()[4:].strip()
            
            if not sys_query:
                full_ai_response = "⚠️  **Uso:** `/sys <pergunta sobre a arquitetura do backend>`"
                sources = []
            else:
                try:
                    sys_engine = build_system_chat_engine(request.provider, request.model)
                    if not sys_engine:
                        full_ai_response = "❌ Erro: O Motor de Sistema não pôde ser iniciado."
                        sources = []
                    else:
                        response = await sys_engine.achat(sys_query)
                        full_ai_response = f"🧠 *Consultando Sistema Meta-RAG...*\n\n{str(response)}"
                        
                        source_nodes = getattr(response, "source_nodes", [])
                        sources = []
                        if source_nodes:
                            for node_w_score in source_nodes:
                                metadata = node_w_score.node.metadata
                                if metadata and metadata.get("file_path"):
                                    import os
                                    filename = os.path.basename(metadata.get('file_path'))
                                    sources.append(Citation(source=f"🛠️ {filename}"))
                                    
                except Exception as e:
                    logger_routes.error(f"Meta-RAG Error: {e}")
                    full_ai_response = f"❌ Erro interno no Meta-RAG: {e}"
                    sources = []
                    
            ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response)
            db.add(ai_msg_db)
            db.commit()
            
            return ChatResponse(response=full_ai_response, sources=sources)
            
        temp_sys_msg = None
        if request.active_document:
            from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
            temp_sys_msg = LlamaMsg(role=MessageRole.USER, content=f"Aqui está o texto do meu documento ativo no Obsidian, APENAS CONSIDERE ele caso minha próxima pergunta tenha a ver com ele. NÃO invente informações se eu não perguntar:\n{request.active_document}")
            engine._memory.put(temp_sys_msg)

        try:
            response = await engine.achat(request.message)
            
            # Gravar a mensagem da IA sincrona
            full_ai_response = str(response)
            ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response, tenant_id=tenant_id)
            db.add(ai_msg_db)
            db.commit()
            
            # Extrai fontes caso existam
            source_nodes = getattr(response, "source_nodes", [])
            citations = []
            if source_nodes:
                for node_w_score in source_nodes:
                    metadata = node_w_score.node.metadata
                    if metadata and "file_path" in metadata:
                        citations.append(Citation(source=metadata["file_path"]))
                        
            return ChatResponse(response=full_ai_response, sources=citations)
        finally:
            if request.active_document and temp_sys_msg:
                try:
                    all_history = engine._memory.get_all()
                    clean_history = [m for m in all_history if m.content != temp_sys_msg.content]
                    engine._memory.chat_store.set_messages(engine._memory.chat_store_key, clean_history)
                except Exception:
                    pass

from .schemas import SessionResponse, FeedbackRequest, SessionUpdateRequest  # noqa: E402
from typing import List  # noqa: E402
from fastapi import HTTPException  # noqa: E402

@router.patch("/sessions/{session_id}", response_model=SessionResponse)
@limiter.limit("60/minute")
async def update_session(request: Request, session_id: int, req: SessionUpdateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Atualiza metadados da sessão, como Título e Diretório (folder_name)."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    
    if req.title is not None:
        session.title = req.title.strip()
    if req.folder_name is not None:
        folder = req.folder_name.strip()
        session.folder_name = folder if folder else None
    if req.tags is not None:
        session.tags = req.tags
        
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}")
@limiter.limit("60/minute")
async def delete_session(request: Request, session_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Remove uma conversa inteira."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    db.delete(session)
    db.commit()
    return {"status": "success"}

@router.get("/sessions", response_model=List[SessionResponse])
@limiter.limit("120/minute")
async def get_all_sessions(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Lista todas as conversas gravadas no SQLite."""
    sessions = db.query(ChatSession).filter(ChatSession.tenant_id == tenant_id).order_by(ChatSession.updated_at.desc()).limit(20).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=SessionResponse)
@limiter.limit("120/minute")
async def get_session_history(request: Request, session_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Busca o histórico completo de uma sessão específica para Replay na UI."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.tenant_id == tenant_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/feedback")
async def save_feedback(req: FeedbackRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Grava o Thumbs Up / Down ou comentário de correção no Database para a AI."""
    msg = db.query(ChatMessage).filter(ChatMessage.id == req.message_id, ChatMessage.tenant_id == tenant_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    msg.thumbs_up = req.thumbs_up
    msg.thumbs_down = req.thumbs_down
    if req.feedback_text:
        msg.feedback_text = req.feedback_text
        
    db.commit()
    return {"status": "success"}

import hashlib  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402
from fastapi import File, UploadFile, Form  # noqa: E402
from .schemas import UploadResponse  # noqa: E402
from .models import DocumentCache  # noqa: E402

@router.post("/upload", response_model=UploadResponse)
@limiter.limit("20/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...), 
    force_overwrite: bool = Form(False),
    rename_if_exists: bool = Form(False),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_user)
):
    """
    Ingests a single document on-the-fly into ChromaDB.
    Handles deduplication using SHA256. 
    Returns 'conflict' if a file with the same name but different content exists.
    """
    from src.config import RAW_DOCS_DIR
    
    raw_dir = Path(RAW_DOCS_DIR)
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    file_size = len(file_content)
    
    # 1. Verificar Hash Exato
    existing_hash = db.query(DocumentCache).filter(DocumentCache.sha256 == file_hash, DocumentCache.tenant_id == tenant_id).first()
    if existing_hash:
        return UploadResponse(
            status="success",
            message="O arquivo já existe no banco de dados com formato e conteúdo idênticos. Nenhuma ação extra é necessária.",
            file_path=existing_hash.file_path,
            sha256=file_hash
        )
        
    # 2. Verificar Colisão de Nome de Arquivo (Conteúdo/Hash diferente)
    target_path = raw_dir / file.filename
    existing_file = db.query(DocumentCache).filter(DocumentCache.file_path == str(target_path.absolute()), DocumentCache.tenant_id == tenant_id).first()
    
    if existing_file and not force_overwrite:
        if rename_if_exists:
            # Auto-rename appending an excerpt of the hash
            stem = target_path.stem
            ext = target_path.suffix
            new_filename = f"{stem}-{file_hash[:6]}{ext}"
            target_path = raw_dir / new_filename
            existing_file = None # É um arquivo novo agora
        else:
            return UploadResponse(
                status="conflict",
                message=f"Um arquivo com o nome '{file.filename}' já existe, mas o conteúdo é diferente. Deseja sobrescrever ou renomear?",
                file_path=str(target_path),
                sha256=file_hash,
                require_action="rename_or_overwrite"
            )
        
    # 3. Salvar no Disco
    with open(target_path, "wb") as buffer:
        buffer.write(file_content)
        
    # 4. Ingerir no ChromaDB dinamicamente usando a thread pool
    from src.ingest import process_single_file
    is_update = bool(existing_file)
    index = await asyncio.to_thread(process_single_file, target_path, is_update)
    
    if not index:
        # Reverte se der erro grave na indexação
        if target_path.exists():
            os.remove(target_path)
        raise HTTPException(status_code=500, detail="Falha ao ingerir o documento no banco vetorial.")
        
    # 5. Salvar DocumentCache no SQLite
    if existing_file:
        existing_file.sha256 = file_hash
        existing_file.file_size = file_size
        db.commit()
    else:
        new_doc = DocumentCache(
            filename=file.filename,
            file_path=str(target_path.absolute()),
            sha256=file_hash,
            file_size=file_size,
            tenant_id=tenant_id
        )
        db.add(new_doc)
        db.commit()

    return UploadResponse(
        status="success",
        message="Arquivo inserido e indexado com sucesso na base de conhecimento.",
        file_path=str(target_path.absolute()),
        sha256=file_hash
    )

def _get_setting_value(db: Session, key: str, default: str, tenant_id: str) -> str:
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key, SystemSettings.tenant_id == tenant_id).first()
    return setting.setting_value if setting and setting.setting_value else default

def _set_setting_value(db: Session, key: str, value: str, tenant_id: str):
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key, SystemSettings.tenant_id == tenant_id).first()
    if setting:
        setting.setting_value = value
    else:
        db.add(SystemSettings(setting_key=key, setting_value=value, tenant_id=tenant_id))

@router.get("/config", response_model=SettingsResponse)
@limiter.limit("120/minute")
def get_settings(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Retrieve dynamic LLM attributes from the database, falling back to .env variables."""
    from config import LLM_PROVIDER, LLM_MODEL, ASSISTANT_PERSONA
    return SettingsResponse(
        llm_provider=_get_setting_value(db, "llm_provider", LLM_PROVIDER, tenant_id),
        llm_model=_get_setting_value(db, "llm_model", LLM_MODEL, tenant_id),
        temperature=float(_get_setting_value(db, "temperature", "0.1", tenant_id)),
        system_prompt=_get_setting_value(db, "system_prompt", ASSISTANT_PERSONA, tenant_id),
        theme=_get_setting_value(db, "theme", "dark", tenant_id),
        persona=_get_setting_value(db, "persona", "default", tenant_id),
        formality=_get_setting_value(db, "formality", "neutral", tenant_id),
        ai_name=_get_setting_value(db, "ai_name", "", tenant_id),
        nickname=_get_setting_value(db, "nickname", "", tenant_id),
        occupation=_get_setting_value(db, "occupation", "", tenant_id),
        about_user=_get_setting_value(db, "about_user", "", tenant_id),
        language=_get_setting_value(db, "language", "Português do Brasil", tenant_id),
        geolocation=_get_setting_value(db, "geolocation", "", tenant_id)
    )

@router.post("/config", response_model=SettingsResponse)
@limiter.limit("60/minute")
def update_settings(request: Request, body_request: SettingsRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Persist the changes in system behavior using key-value entries in the database."""
    try:
        _set_setting_value(db, "llm_provider", body_request.llm_provider, tenant_id)
        _set_setting_value(db, "llm_model", body_request.llm_model, tenant_id)
        _set_setting_value(db, "temperature", str(body_request.temperature), tenant_id)
        _set_setting_value(db, "system_prompt", body_request.system_prompt, tenant_id)
        _set_setting_value(db, "theme", body_request.theme, tenant_id)
        _set_setting_value(db, "persona", body_request.persona, tenant_id)
        _set_setting_value(db, "formality", body_request.formality, tenant_id)
        _set_setting_value(db, "ai_name", body_request.ai_name, tenant_id)
        _set_setting_value(db, "nickname", body_request.nickname, tenant_id)
        _set_setting_value(db, "occupation", body_request.occupation, tenant_id)
        _set_setting_value(db, "about_user", body_request.about_user, tenant_id)
        _set_setting_value(db, "language", body_request.language, tenant_id)
        _set_setting_value(db, "geolocation", body_request.geolocation, tenant_id)
        db.commit()
    except Exception as e:
        db.rollback()
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    
    # Fake a request to reuse get_settings which now expects a Request object
    try:
        return get_settings(request=request, db=db, tenant_id=tenant_id)
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail="Error inside get_settings: " + str(e))

@router.get("/ollama/models")
@limiter.limit("60/minute")
async def list_ollama_models(request: Request):
    """Fetches the list of locally pulled models from the Ollama server."""
    import httpx
    from src.config import OLLAMA_BASE_URL
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return {"models": models}
    except Exception as e:
        # Fallback to empty list or known models if Ollama is unreachable
        print(f"Failed to fetch Ollama models: {e}")
        return {"models": []}

from pydantic import BaseModel

class PullModelRequest(BaseModel):
    model: str

def background_ollama_pull(model_name: str, base_url: str):
    import httpx
    try:
        print(f"Buscando modelo Ollama {model_name} remotamente...")
        with httpx.Client(timeout=600.0) as client:
            client.post(f"{base_url}/api/pull", json={"name": model_name, "stream": False})
        print(f"Download de {model_name} finalizado via background task.")
    except Exception as e:
        print(f"Erro efetuando pull do modelo {model_name}: {e}")

@router.post("/ollama/pull")
@limiter.limit("10/minute")
async def pull_ollama_model(request: Request, body_request: PullModelRequest, tenant_id: str = Depends(get_current_user)):
    """
    Inicia o pull de um modelo Ollama e retorna o progresso do download via SSE (Server-Sent Events).
    """
    from src.config import OLLAMA_BASE_URL
    import httpx
    import json
    from fastapi.responses import StreamingResponse

    async def event_generator():
        try:
            # Conexão Async com timeout grande para downloads massivos (1h = 3600s)
            async with httpx.AsyncClient(timeout=3600.0) as client:
                async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/pull", json={"name": body_request.model, "stream": True}) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_lines():
                        if chunk:
                            try:
                                # Ollama envia um JSON para cada atualização de progresso
                                data = json.loads(chunk)
                                # Encapsulando o chunk original dentro do formato SSE do nosso frontend
                                yield f"data: {json.dumps(data)}\n\n"
                                
                                # Se terminou o download com sucesso
                                if data.get("status") == "success":
                                    break
                            except json.JSONDecodeError:
                                print(f"Erro no parse de Chunk de Pull do Ollama: {chunk}")
                                yield f"data: {json.dumps({'status': 'error', 'error': 'JSON Chunk Error'})}\n\n"
                                continue
        except httpx.HTTPStatusError as e:
             yield f"data: {json.dumps({'status': 'error', 'error': f'Ollama HTTP Error: {e.response.status_code}'})}\n\n"
        except Exception as e:
             yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
        finally:
             yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/vault/tree")
async def get_vault_tree(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Retorna a árvore de arquivos do Sensus Vault (Markdown) para a Sidebar do Frontend Vue.
    Agrupa os arquivos por pasta pai.
    """
    import os
    # Temporariamente forçando o tenant 'default' que The Mom usa
    docs = db.query(SensusDocumentModel).filter(SensusDocumentModel.tenant_id == "default").all()
    
    # Estrutura: { "folder_name": [ { "name": "file.md", "path": "/full...", "vector_id": "xyz", "synced": true } ] }
    tree = {"": []} # Raiz (Root)
    
    for doc in docs:
        filename = os.path.basename(doc.file_path)
        # Tenta inferir a pasta pegando o penúltimo elemento do path original do Cofre (SharedBrain)
        path_parts = doc.file_path.split(os.sep)
        folder = ""
        if len(path_parts) > 2:
            possible_folder = path_parts[-2]
            # Se a pasta imediatamente anterior não for o vault base, agrupa nela
            if possible_folder.lower() not in ["vault", "sharedbrain", "data"]:
                folder = possible_folder
                
        if folder not in tree:
            tree[folder] = []
            
        tree[folder].append({
            "name": filename,
            "path": doc.file_path,
            "tags": doc.extracted_tags,
            "has_vector": doc.vector_id is not None,
            "id": doc.id
        })
        
    return tree

@router.get("/vault/document/{doc_id}")
async def get_vault_document(doc_id: str, db: Session = Depends(get_db)):
    """Busca o conteúdo cru do respectivo markdown no disco."""
    import os
    from fastapi import HTTPException
    
    doc = db.query(SensusDocumentModel).filter(SensusDocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado no DB")
        
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado no cofre")
        
    with open(doc.file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    return {
        "id": doc.id,
        "name": os.path.basename(doc.file_path),
        "path": doc.file_path,
        "content": content,
        "tags": doc.extracted_tags,
        "has_vector": doc.vector_id is not None,
        "vector_id": doc.vector_id
    }

@router.put("/vault/document/{doc_id}")
async def update_vault_document(doc_id: str, request: DocumentUpdateRequest, db: Session = Depends(get_db)):
    """Atualiza o conteúdo físico do markdown no disco. O Watchdog 'The Mom' se encarrega do sync SQLite e Vetor."""
    import os
    from fastapi import HTTPException
    
    doc = db.query(SensusDocumentModel).filter(SensusDocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado no DB")

    with open(doc.file_path, 'w', encoding='utf-8') as f:
        f.write(request.content)
        
    return {"message": "Document saved successfully", "id": doc.id}

class TableCalcRequest(BaseModel):
    cells: dict[str, str]
    deleted_column: str | None = None

class TableCalcResponse(BaseModel):
    results: dict[str, str]
    errors: dict[str, str]

@router.post("/vault/table/evaluate", response_model=TableCalcResponse)
@limiter.limit("60/minute")
async def evaluate_table(request: Request, body: TableCalcRequest, tenant_id: str = Depends(get_current_user)):
    """
    Roteia o Input de Fórmulas da Tabela Vue (TipTap) para o AST Motor (The Accountant).
    Avalia em tempo-real somas, referências e propaga Erros de Deleção.
    """
    from src.core.the_accountant import TheAccountant
    
    engine = TheAccountant()
    
    # Registra todas as células na RAM (Constrói a Grafo de Dependências)
    for coord, content in body.cells.items():
        engine.register_cell(coord, content)
        
    updates = {}
    errors = {}
    
    # Se o front-end notificar que uma Coluna foi deletada (Ex: 'B')
    if body.deleted_column:
        # Puxa o efeito cascata no DAG
        cascade_updates = engine.handle_cell_deletion(body.deleted_column)
        for c_id, n_cont in cascade_updates:
            updates[c_id] = n_cont
            errors[c_id] = "#REF!"
            
    # Avalia matematicamente a nova topologia da tabela AST
    eval_results = engine.evaluate_all()
    
    # Processa os resultados para enviar ao Frontend
    final_updates = dict(updates)
    
    for c_id, val in eval_results.items():
        val_str = str(val)
        if "#REF!" in val_str:
            val_str = "#REF!"
            
        # Sobrescreve apenas se não for um override manual via detonação
        if c_id not in final_updates or final_updates[c_id] != "#REF!":
            final_updates[c_id] = val_str

    for c_id, val_str in final_updates.items():
        if val_str in ["#REF!", "#CIRCULAR_REF!", "#ERROR!", "#DIV/0!"]:
            errors[c_id] = val_str
            
    return TableCalcResponse(results=final_updates, errors=errors)

@router.get("/vault/search")
async def search_vault(q: str, db: Session = Depends(get_db)):
    """Pesquisa heurística super-rápida via SQLite LIKE no Título, Resumo Semântico e Tags."""
    import os
    from sqlalchemy import or_
    
    # Limita a busca em 10 resultados para a Sophi Bar não travar
    query = f"%{q}%"
    docs = db.query(SensusDocumentModel).filter(
        SensusDocumentModel.tenant_id == "default",
        or_(
            SensusDocumentModel.file_path.ilike(query),
            SensusDocumentModel.semantic_summary.ilike(query)
        )
    ).limit(10).all()

    # Se a filtragem JSON do SQLite for complexa, fazemos try-catch ou filtramos na mão
    
    results = []
    for doc in docs:
        results.append({
            "id": doc.id,
            "name": os.path.basename(doc.file_path),
            "summary": doc.semantic_summary or "Sem resumo semântico gerado ainda.",
            "tags": doc.extracted_tags,
            "has_vector": doc.vector_id is not None
        })
        
    return results

@router.get("/vault/recent")
async def get_recent_documents(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Retorna os documentos ordenados por modificação (Recent Activities)"""
    import os
    docs = db.query(SensusDocumentModel).filter(
        SensusDocumentModel.tenant_id == tenant_id
    ).order_by(SensusDocumentModel.updated_at.desc()).limit(15).all()
    
    results = []
    for doc in docs:
        results.append({
            "name": os.path.basename(doc.file_path),
            "path": doc.file_path,
            "updated_at": doc.updated_at.isoformat()
        })
    return results

@router.get("/vault/tasks")
async def get_vault_tasks(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Escaneia todos os documentos atrás de Tarefas Pendentes `[ ]`"""
    docs = db.query(SensusDocumentModel).filter(
        SensusDocumentModel.tenant_id == tenant_id
    ).all()
    
    tasks = []
    for doc in docs:
        if not doc.extracted_todos: 
            continue
            
        for todo in doc.extracted_todos:
            # Filtra apenas os pendentes (excluindo os [x])
            if todo.startswith("[x]") or todo.startswith("[X]"):
                continue
            
            # Remove o cast bruto "[ ] " deixando apenas o texto nativo
            clean_text = todo[3:].strip()
            if clean_text:
                tasks.append({
                    "text": clean_text,
                    "file": doc.file_path
                })
    return tasks

# ---------------------------------------------------------
# MCP (Model Context Protocol) Endpoints - Phase 21
# ---------------------------------------------------------
from pydantic import BaseModel, Field

class MCPToolRequest(BaseModel):
    tool: str
    parameters: dict = Field(default_factory=dict)

@router.post("/mcp/tool")
async def execute_mcp_tool(request: Request, body: MCPToolRequest):
    """
    Executa ferramentas expostas via MCP (VSCode OpenCode / Cline).
    Permite que o Editor consuma o RAG e o Context7 do Sovereign Pair.
    """
    import os
    import json
    
    if body.tool == "sensus_vault_search":
        # Simula uma busca heurística rápida para o Coder na IDE
        query = body.parameters.get("query", "")
        # Em produção, chamaremos o The Dad Vector Search, mas por ora um simples heuristics
        return {"result": f"Busca MCP recebida para '{query}'. (Integração do The Dad em andamento na Sprint 21)."}
        
    elif body.tool == "sensus_project_context":
        from src.config import VAULT_DIR
        project = body.parameters.get("project_name", "default")
        
        # Mapeamento do Context7 (Árvore de arquivos básica por hora)
        tree = {}
        target_dir = VAULT_DIR
        
        if os.path.exists(target_dir):
            for root, dirs, files in os.walk(target_dir):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                rel_path = os.path.relpath(root, target_dir)
                if rel_path == '.':
                    tree['/'] = files
                else:
                    tree[rel_path] = files
                    
        return {
            "project": project,
            "architecture": "Cibrid Agentic Architecture (Phase 21)",
            "context7_depth": "Layer 3 (File Tree Map / Structural Awareness)",
            "tree": tree
        }

    raise HTTPException(status_code=404, detail=f"Tool '{body.tool}' not found in MCP registry.")
