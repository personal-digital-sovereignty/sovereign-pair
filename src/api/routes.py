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
            
            for token in response.response_gen:
                # Enviando tokens em formato padrão SSE
                yield f"data: {json.dumps({'content': token})}\n\n"
                
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
                nl = "\\n" # Evitar escaping quebra no json dumping
                sources_str = f"{nl}{nl}**Fontes:**{nl}" + f"{nl}".join([f"  - {s}" for s in sorted(sources)])
                yield f"data: {json.dumps({'content': sources_str})}\n\n"
                
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        # Modo Blocante
        response = await asyncio.to_thread(engine.chat, request.message)
        
        sources = set()
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
