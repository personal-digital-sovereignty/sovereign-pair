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
    body_request: dict,
    db: Session = Depends(get_db)
):
    """
    OpenAI-Compatible proxy endpoint isolado sem a dependência do token Bearer do Frontend Sovereign (tenant_id).
    Recebe requests do OpenCode e direciona silenciosamente para os LLMs locais ou remoto mTLS.
    """
    from src.api.schemas import (
        OpenAIChatRequest, OpenAIChatResponse, OpenAIChatChoice, OpenAIChatChoiceMessage, 
        OpenAIChatChunkResponse, OpenAIChatChunkChoice, OpenAIChatChunkDelta, OpenAITokenUsage
    )
    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
    from src.engine_builder import resolve_dynamic_llm
    from src.config import get_default_llm
    from src.api.routes import _get_setting_value
    
    # Valida usando o Modelo Pydantic para OpenAI
    parsed_body = OpenAIChatRequest(**body_request)
    
    # Mocking tenant_id as default for local extensions bypassing auth
    tenant_id = "default"
    
    # 1. Recuperar configurações do DB (para chaves customizadas se usar remotos)
    db_provider = _get_setting_value(db, "llm_provider", "openai", tenant_id)
    api_keys = {
        "openai_api_key": _get_setting_value(db, "openai_api_key", "", tenant_id),
        "anthropic_api_key": _get_setting_value(db, "anthropic_api_key", "", tenant_id),
        "gemini_api_key": _get_setting_value(db, "gemini_api_key", "", tenant_id),
        "custom_ollama_url": _get_setting_value(db, "custom_ollama_url", "", tenant_id)
    }
    
    # 2. Roteamento Inteligente (Baseado no modelo requisitado ou Fallback local)
    target_model = parsed_body.model
    # Se o modelo requisitado referenciar Llama, Qwen ou DeepSeek, forçamos Ollama local
    target_provider = "ollama" if any(k in target_model.lower() for k in ["llama", "qwen", "mistral", "deepseek"]) else db_provider
    
    active_llm = resolve_dynamic_llm(target_provider, target_model, get_default_llm(), api_keys)
    
    # 3. Converter histórico do formato OpenAI para LlamaIndex
    llama_msgs = []
    for msg in parsed_body.messages:
        role = MessageRole.USER if msg.role == "user" else MessageRole.ASSISTANT
        if msg.role == "system": role = MessageRole.SYSTEM
        llama_msgs.append(LlamaMsg(role=role, content=msg.content))
        
    chat_id = "chatcmpl-" + str(uuid.uuid4())
    created_ts = int(time.time())

    # 4. Modo Streaming (SSE Data Generator)
    if parsed_body.stream:
        async def openai_event_generator():
            try:
                # Dispara astream no LlamaIndex Puro
                response_gen = await active_llm.astream_chat(llama_msgs)
                async for token in response_gen:
                    if token.delta:
                        chunk_choice = OpenAIChatChunkChoice(
                            index=0,
                            delta=OpenAIChatChunkDelta(role="assistant", content=token.delta),
                            finish_reason=None
                        )
                        chunk_response = OpenAIChatChunkResponse(
                            id=chat_id,
                            created=created_ts,
                            model=target_model,
                            choices=[chunk_choice]
                        )
                        yield f"data: {chunk_response.model_dump_json(exclude_none=True)}\n\n"
                
                # Signal final chunk with finish_reason
                final_choice = OpenAIChatChunkChoice(
                    index=0,
                    delta=OpenAIChatChunkDelta(),
                    finish_reason="stop"
                )
                final_response = OpenAIChatChunkResponse(
                    id=chat_id,
                    created=created_ts,
                    model=target_model,
                    choices=[final_choice]
                )
                yield f"data: {final_response.model_dump_json(exclude_none=True)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                import logging
                logging.error(f"[OpenCode Proxy Error STREAM]: {e}")
                err_choice = OpenAIChatChunkChoice(index=0, delta=OpenAIChatChunkDelta(content=f"\n\n❌ Erro no Proxy Sovereign Pair: {str(e)}"), finish_reason="stop")
                err_res = OpenAIChatChunkResponse(id=chat_id, created=created_ts, model=target_model, choices=[err_choice])
                yield f"data: {err_res.model_dump_json(exclude_none=True)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(openai_event_generator(), media_type="text/event-stream")

    # 5. Modo Síncrono (JSON Padrão)
    else:
        try:
            response = await active_llm.achat(llama_msgs)
            
            choice_msg = OpenAIChatChoiceMessage(role="assistant", content=str(response.message.content))
            choice = OpenAIChatChoice(index=0, message=choice_msg, finish_reason="stop")
            
            # TODO: Tokenizer metric counts
            usage = OpenAITokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            
            # Formata utilizando os Schema Pydantics novos
            final_pydantic_res = OpenAIChatResponse(
                id=chat_id,
                created=created_ts,
                model=target_model,
                choices=[choice],
                usage=usage
            )
            return final_pydantic_res
        except Exception as e:
            from fastapi.responses import JSONResponse
            import logging
            logging.error(f"[OpenCode Proxy Error SYNC]: {e}")
            return JSONResponse(status_code=500, content={"error": {"message": f"Proxy Error: {str(e)}", "type": "proxy_error"}})

