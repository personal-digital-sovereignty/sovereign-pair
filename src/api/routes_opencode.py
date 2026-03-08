from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from .database import get_db
import time
import json
import uuid

# Importando o limiter configurado no main.py
try:
    from .main import limiter
except ImportError:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/chat/completions")
@limiter.limit("120/minute")
async def opencode_chat_completions(
    request: Request,
    body: dict,
    db: Session = Depends(get_db)
):
    """
    OpenAI-Compatible Endpoint Proxy isolado sem a dependência do token Bearer do Frontend Sovereign (tenant_id).
    Recebe requests do OpenCode e direciona silenciosamente para os LLMs locais.
    """
    from src.api.schemas import OpenAIChatRequest
    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
    from src.engine_builder import resolve_dynamic_llm
    from src.config import get_default_llm
    from src.api.routes import _get_setting_value
    
    parsed_body = OpenAIChatRequest(**body)
    
    # Mocking tenant_id as default for local extensions
    tenant_id = "default"
    
    llama_msgs = []
    for msg in parsed_body.messages:
        role = MessageRole.USER
        if msg.role == "system":
            role = MessageRole.SYSTEM
        elif msg.role == "assistant":
            role = MessageRole.ASSISTANT
            
        llama_msgs.append(LlamaMsg(role=role, content=msg.content))
        
    db_provider = _get_setting_value(db, "llm_provider", "openai", tenant_id)
    target_provider = db_provider
    target_model = parsed_body.model
    
    api_keys = {
        "openai_api_key": _get_setting_value(db, "openai_api_key", "", tenant_id),
        "anthropic_api_key": _get_setting_value(db, "anthropic_api_key", "", tenant_id),
        "gemini_api_key": _get_setting_value(db, "gemini_api_key", "", tenant_id),
        "custom_ollama_url": _get_setting_value(db, "custom_ollama_url", "", tenant_id)
    }
    
    # Auto-routing para ollama local se for modelo aberto
    if any(k in target_model.lower() for k in ["llama", "qwen", "mistral"]):
        target_provider = "ollama"
    elif "coder" in target_model.lower():
        target_provider = "coder"
    active_llm = resolve_dynamic_llm(target_provider, target_model, get_default_llm(), api_keys)

    if parsed_body.stream:
        async def openai_event_generator():
            try:
                response_gen = await active_llm.astream_chat(llama_msgs)
                chat_id = "chatcmpl-" + str(uuid.uuid4())
                created = int(time.time())
                
                async for token in response_gen:
                    if token.delta:
                        chunk = {
                            "id": chat_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": target_model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"content": token.delta},
                                    "finish_reason": None
                                }
                            ]
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        
                final_chunk = {
                    "id": chat_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": target_model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
                }
                yield f"data: {json.dumps(final_chunk)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                import logging
                logging.error(f"Error in OpenAI proxy stream: {e}")
                err_chunk = {"error": {"message": str(e), "type": "server_error"}}
                yield f"data: {json.dumps(err_chunk)}\n\n"
                
        return StreamingResponse(openai_event_generator(), media_type="text/event-stream")
    else:
        response = await active_llm.achat(llama_msgs)
        return {
            "id": "chatcmpl-" + str(uuid.uuid4()),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": target_model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": str(response)},
                    "finish_reason": "stop"
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
