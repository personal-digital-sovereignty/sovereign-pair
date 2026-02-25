import asyncio
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from .schemas import ChatRequest, ChatResponse, Citation
from .dependencies import get_chat_engine

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, engine=Depends(get_chat_engine)):
    """
    Endpoint principal para conversar com o Agente via RAG local.
    Pode retornar tanto um JSON blocante quanto um Event-Stream (SSE) para digitação em tempo real.
    """
    if request.stream:
        async def event_generator():
            # Executar query_engine via thread para não bloquear o Async Loop do ASGI
            response = await asyncio.to_thread(engine.stream_chat, request.message)
            
            if isinstance(response, str) or not hasattr(response, 'response_gen'):
                yield f"data: {json.dumps({'content': str(response)})}\n\n"
            else:
                full_response = ""
                for token in response.response_gen:
                    full_response += token
                    # Enviando tokens em formato padrão SSE
                    yield f"data: {json.dumps({'content': token})}\n\n"
                
                # Heurística para ocultar fontes em respostas triviais (saudações, data) ou não-encontradas
                texto = full_response.lower()
                is_trivial_or_not_found = (
                    "não encontrei essa informação" in texto or
                    "não há informações" in texto or
                    "nenhuma menção" in texto or
                    (len(texto) < 150 and not any(word in texto for word in ["contexto", "documento", "arquivo", "fonte", "projeto"]))
                )
                
                if not is_trivial_or_not_found:
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
                        nl = "\n"
                        sources_str = f"{nl}{nl}**Fontes:**{nl}" + f"{nl}".join([f"  - {s}" for s in sorted(sources)])
                        yield f"data: {json.dumps({'content': sources_str})}\n\n"
                        
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Modo Blocante
        response = await asyncio.to_thread(engine.chat, request.message)
        
        texto = str(response).lower()
        is_trivial_or_not_found = (
            "não encontrei essa informação" in texto or
            "não há informações" in texto or
            "nenhuma menção" in texto or
            (len(texto) < 150 and not any(word in texto for word in ["contexto", "documento", "arquivo", "fonte", "projeto"]))
        )
        
        sources = set()
        if not is_trivial_or_not_found:
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
