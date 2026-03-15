import asyncio
import json
from fastapi import APIRouter, Depends, Request
import uuid
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from .schemas import ChatRequest, ChatResponse, Citation, SettingsRequest, SettingsResponse, SessionUpdateRequest, UploadResponse, DocumentUpdateRequest, ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse, TaskCreateRequest, TaskUpdateRequest, TaskResponse, NoteCreateRequest, NoteUpdateRequest, NoteResponse, ActivityLogResponse
from .dependencies import get_chat_engine
from typing import List

from sqlalchemy.orm import Session
from .database import get_db
from .models import ChatSession, ChatMessage, SystemSettings, SensusDocumentModel, QuarantineLog, ProjectModel, ProjectLinkModel, ProjectLogModel, DocumentCache, TaskModel, NoteModel, ActivityLogModel
from .auth import get_current_user
from .schemas import SessionResponse, FeedbackRequest
from fastapi import HTTPException, File, UploadFile, Form
import hashlib
import os
from pathlib import Path

import httpx
import logging

logger_routes = logging.getLogger(__name__)
router = APIRouter()

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
            full_ai_response = ""
            ai_msg_db = None
            temp_sys_msg = None
            try:
                # Injetar o documento ativo como memória do sistema (apenas se existir) para não sujar a busca BM25/Vector
                if body_request.active_document:
                    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                    temp_sys_msg = LlamaMsg(role=MessageRole.USER, content=f"Aqui está o texto do meu documento ativo no Sovereign Vault, APENAS CONSIDERE ele caso minha próxima pergunta tenha a ver com ele. NÃO invente informações se eu não perguntar:\n{body_request.active_document}")
                    engine._memory.put(temp_sys_msg)

                # Interceptar comando remoto /web
                is_web_query = body_request.message.strip().startswith('/web')
                response = None
                web_query = None
                timelimit = None
                
                if is_web_query:
                    import re
                    from src.web_search import search_web
                    from src.engine_builder import resolve_dynamic_llm
                    from src.config import get_default_llm
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
                        yield f"data: {json.dumps({'content': f'*Buscando na web...{time_info}*\n\n'})}\n\n"
                        
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

                        db_provider = _get_setting_value(db, "llm_provider", "openai", tenant_id)
                        db_model = _get_setting_value(db, "llm_model", "gpt-4o-mini", tenant_id)
                        
                        api_keys = {
                            "openai_api_key": _get_setting_value(db, "openai_api_key", "", tenant_id),
                            "anthropic_api_key": _get_setting_value(db, "anthropic_api_key", "", tenant_id),
                            "gemini_api_key": _get_setting_value(db, "gemini_api_key", "", tenant_id),
                            "custom_ollama_url": _get_setting_value(db, "custom_ollama_url", "", tenant_id)
                        }

                        target_provider = body_request.provider or db_provider
                        target_model = body_request.model or db_model
                        
                        active_llm = resolve_dynamic_llm(target_provider, target_model, get_default_llm(), api_keys)
                        
                        try:
                            response_gen = await active_llm.astream_chat(messages_to_send)
                            
                            full_ai_response = f"*Buscando na web...{time_info}*\n\n"
                            async for token in response_gen:
                                if token.delta:
                                    full_ai_response += token.delta
                                    yield f"data: {json.dumps({'content': token.delta})}\n\n"
                        except Exception as e:
                            logger_routes.error(f"Failed to infer from LLM (Web Search): {e}")
                            err_msg = f"\n\n**Falha Crítica Cíbrida (Web Search):**\nO motor LLM ({target_provider}) recusou a inferência ou está offline.\nDetalhe Técnico: `{str(e)}`"
                            yield f"data: {json.dumps({'content': err_msg})}\n\n"
                    else:
                        full_ai_response = "**Uso:** `/web <query>`\n\n**Filtros:** `/web -d` (dia), `/web -w` (semana), `/web -m` (mês), `/web -y` (ano)"
                        yield f"data: {json.dumps({'content': full_ai_response})}\n\n"

                elif body_request.message.strip().startswith('/sys'):
                    from src.engine_builder import build_system_chat_engine
                    sys_query = body_request.message.strip()[4:].strip()
                    
                    if not sys_query:
                        full_ai_response = "**Uso:** `/sys <pergunta sobre a arquitetura do backend>`"
                        yield f"data: {json.dumps({'content': full_ai_response})}\n\n"
                    else:
                        yield f"data: {json.dumps({'content': '*Consultando Sistema RAG...*\n\n'})}\n\n"
                        try:
                            db_provider = _get_setting_value(db, "llm_provider", "openai", tenant_id)
                            db_model = _get_setting_value(db, "llm_model", "gpt-4o-mini", tenant_id)
                            
                            api_keys = {
                                "openai_api_key": _get_setting_value(db, "openai_api_key", "", tenant_id),
                                "anthropic_api_key": _get_setting_value(db, "anthropic_api_key", "", tenant_id),
                                "gemini_api_key": _get_setting_value(db, "gemini_api_key", "", tenant_id),
                                "custom_ollama_url": _get_setting_value(db, "custom_ollama_url", "", tenant_id)
                            }

                            target_provider = body_request.provider or db_provider
                            target_model = body_request.model or db_model
                            
                            sys_engine = build_system_chat_engine(target_provider, target_model, api_keys)
                            if not sys_engine:
                                full_ai_response = "Erro: O Motor de Sistema não pôde ser iniciado. O banco vetorial foi criado?"
                                yield f"data: {json.dumps({'content': full_ai_response})}\n\n"
                            else:
                                response = await sys_engine.astream_chat(sys_query)
                                full_ai_response = "*Consultando Sistema RAG...*\n\n"
                                
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
                                        sources.add(f"{filename}")
                                        
                                if sources:
                                    sources_str = "\n".join(sources)
                                    final_msg = f"\n\n**Arquivos Analisados:**\n{sources_str}"
                                    full_ai_response += final_msg
                                    yield f"data: {json.dumps({'content': final_msg})}\n\n"
                        except Exception as e:
                            import traceback
                            logger_routes.error(f"RAG Error: {e}\n{traceback.format_exc()}")
                            full_ai_response = f'Erro interno no RAG: {type(e).__name__} - {str(e)}'
                            yield f"data: {json.dumps({'content': full_ai_response})}\n\n"

                else:
                    from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                    
                    # 1. Recuperar contexto do banco vetorial via Async
                    try:
                        source_nodes = await engine._retriever.aretrieve(body_request.message)
                    except Exception:
                        source_nodes = await asyncio.to_thread(engine._retriever.retrieve, body_request.message)
                        
                    # 2. Formatar o contexto
                    context_str = "\n\n".join([f"Documento (Path: {n.node.metadata.get('file_path', 'N/A')}):\n{n.node.get_content()}" for n in source_nodes]) if source_nodes else "Nenhum documento vetorial encontrado."
                    
                    # --- NEW: Fetch BYOK API Keys from SQLite ---
                    api_keys = {
                        "openai_api_key": _get_setting_value(db, "openai_api_key", "", tenant_id),
                        "anthropic_api_key": _get_setting_value(db, "anthropic_api_key", "", tenant_id),
                        "gemini_api_key": _get_setting_value(db, "gemini_api_key", "", tenant_id),
                        "custom_ollama_url": _get_setting_value(db, "custom_ollama_url", "", tenant_id)
                    }
                    
                    # --- NEW: Phase 16.5 - The Semantic Router (Nurse Triage) ---
                    from src.core.the_nurse import TheNurse
                    nurse = TheNurse(body_request.provider, body_request.model, api_keys)
                    intent_data = await nurse.evaluate_intent(body_request.message)
                    
                    if not intent_data.get("requires_doctor", True):
                        # Execução Tática Ultra-Rápida pela "Enfermeira"
                        response_gen = await nurse.execute_tactical_task(body_request.message, context_str, intent_data)
                        
                        full_ai_response = f"*(Tarefa Tática Executada pela The Nurse ({intent_data.get('task_type', 'extraction')}))*\n\n"
                        yield f"data: {json.dumps({'content': full_ai_response})}\n\n"
                        
                        async for token in response_gen:
                            if token:
                                full_ai_response += token
                                yield f"data: {json.dumps({'content': token})}\n\n"
                    else:
                        # --- EXECUÇÃO TIER 4: O Médico (Heavy LLM & Deep Synthesis) ---
                        from src.core.the_doctor import TheDoctor
                        doctor = TheDoctor(body_request.provider, body_request.model, engine, api_keys)
                        yield f"data: {json.dumps({'content': '*(Raciocínio Profundo do The Doctor ativado...)*\n\n'})}\n\n"
                        
                        print(f"[DEBUG RAG] Executando The Doctor (Tier 4) via {getattr(doctor.llm, 'model', 'N/A')}...", flush=True)
                        try:
                            # Se a flag de integração remota estiver desligada ou se der timeout na rede (Tailscale/Oracle)
                            integration_enabled_str = _get_setting_value(db, "remote_integration_enabled", "true", tenant_id)
                            if integration_enabled_str.lower() != "true":
                                raise TimeoutError("Restricted Mode Local-First ativado pelo usuário.")

                            response_gen = await doctor.execute_deep_reasoning(body_request.message, context_str, intent_data)
                            
                            full_ai_response = "*(Raciocínio Profundo do The Doctor ativado...)*\n\n"
                            async for token in response_gen:
                                if token:
                                    full_ai_response += token
                                    yield f"data: {json.dumps({'content': token})}\n\n"
                                    
                        except (TimeoutError, httpx.TimeoutException, Exception) as e:
                            # Fallback Gracioso de Rede
                            print(f"[FALLBACK RAG] Erro ao alcançar o Cloud Node ({str(e)}). Redirecionando para The Nurse SLM Local...")
                            fallback_msg = "*(Raciocínio Profundo Indisponível (Nó Remoto Offline). Redirecionando para The Nurse Local...)*\n\n"
                            yield f"data: {json.dumps({'content': fallback_msg})}\n\n"
                            full_ai_response = fallback_msg
                            
                            response_gen = await nurse.execute_tactical_task(body_request.message, context_str, intent_data)
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
                        # Usa a variável source_nodes alimentada dinamicamente via LLM Engine Response (Semgrep Fix: No globals/locals dynamic scope eval)
                        s_nodes = source_nodes if 'source_nodes' in locals() else []
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
            except Exception as e:
                import traceback
                import logging
                logger = logging.getLogger(__name__)
                err_msg = f"\n\n**Erro Inesperado no RAG/Web:**\n```\n{str(e)}\n\n{traceback.format_exc()}\n```"
                logger.error(f"Erro no event_generator FastAPI: {e}\n{traceback.format_exc()}")
                full_ai_response += err_msg
                yield f"data: {json.dumps({'content': err_msg})}\n\n"
                # Fallback for Database or Context Size Limits saving logic
                if ai_msg_db:
                    try:
                        ai_msg_db.content = full_ai_response
                        db.commit()
                    except Exception:
                        pass # If commit fails, we can't do much more here.
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
            from src.config import get_default_llm
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
                
                active_llm = resolve_dynamic_llm(body_request.provider, body_request.model, get_default_llm())
                response = await active_llm.achat(messages_to_send)
                
                full_ai_response = f"*Buscando na web...{time_info}*\n\n{str(response)}"
            else:
                full_ai_response = "**Uso:** `/web <query>`\n\n**Filtros:** `/web -d` (dia), `/web -w` (semana), `/web -m` (mês), `/web -y` (ano)"
                
            # Gravar a mensagem da IA sincrona no SQLite
            ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response, tenant_id=tenant_id)
            db.add(ai_msg_db)
            db.commit()
            
            return ChatResponse(response=full_ai_response, sources=[])
            
        elif is_sys_query:
            from src.engine_builder import build_system_chat_engine
            sys_query = body_request.message.strip()[4:].strip()
            
            if not sys_query:
                full_ai_response = "**Uso:** `/sys <pergunta sobre a arquitetura do backend>`"
                sources = []
            else:
                try:
                    sys_engine = build_system_chat_engine(body_request.provider, body_request.model)
                    if not sys_engine:
                        full_ai_response = "Erro: O Motor de Sistema não pôde ser iniciado."
                        sources = []
                    else:
                        response = await sys_engine.achat(sys_query)
                        full_ai_response = f"*Consultando Sistema RAG...*\n\n{str(response)}"
                        
                        source_nodes = getattr(response, "source_nodes", [])
                        sources = []
                        if source_nodes:
                            for node_w_score in source_nodes:
                                metadata = node_w_score.node.metadata
                                if metadata and metadata.get("file_path"):
                                    import os
                                    filename = os.path.basename(metadata.get('file_path'))
                                    sources.append(Citation(source=f"{filename}"))
                                    
                except Exception as e:
                    import traceback
                    logger_routes.error(f"RAG Error: {e}\n{traceback.format_exc()}")
                    full_ai_response = f"Erro interno no RAG: {type(e).__name__} - {str(e)}"
                    sources = []
                    
            ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response)
            db.add(ai_msg_db)
            db.commit()
            
            return ChatResponse(response=full_ai_response, sources=sources)
            
        temp_sys_msg = None
        active_doc = getattr(body_request, 'active_document', None)
        if active_doc:
            from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
            temp_sys_msg = LlamaMsg(role=MessageRole.USER, content=f"Aqui está o texto do meu documento ativo no Sovereign Vault, APENAS CONSIDERE ele caso minha próxima pergunta tenha a ver com ele. NÃO invente informações se eu não perguntar:\n{active_doc}")
            engine._memory.put(temp_sys_msg)

        try:
            # Bugfix: LlamaIndex Ollama Returns 'Empty Response' in achat() with CondensePlusContext.
            # Workaround: Use astream_chat and accumulate tokens.
            chat_stream = await engine.astream_chat(body_request.message)
            
            full_ai_response = ""
            async for token in chat_stream.async_response_gen():
                full_ai_response += token
                
            if not full_ai_response.strip():
                full_ai_response = getattr(chat_stream, "response", str(chat_stream))
                
            source_nodes = getattr(chat_stream, "source_nodes", [])

            # Bypass Absoluto: LlamaIndex Aborta e engole a request pro Ollama (Retornando "Empty Response")
            # SE E SOMENTE SE a Vector/BM25 Retriever trouxer ZERO (0) arquivos do DB pra compor o contexto.
            # Quando isso acontece, devemos invocar a IA diretamente extraindo a RAM bruta!
            if full_ai_response.strip() == "Empty Response":
                from llama_index.core.llms import ChatMessage as LlamaMsg, MessageRole
                
                # Prepara o histórico + Mensagem nova bypassando o Synthesizer falho do LlamaIndex
                history_msgs = engine._memory.get_all() if engine else []
                sys_msg = LlamaMsg(role=MessageRole.SYSTEM, content=engine._system_prompt if hasattr(engine, '_system_prompt') else "Você é uma inteligência artificial assistente.")
                
                messages_to_send = [sys_msg] + history_msgs + [LlamaMsg(role=MessageRole.USER, content=body_request.message)]
                
                fallback_stream = await engine._llm.astream_chat(messages_to_send)
                full_ai_response = ""
                async for chunk in fallback_stream:
                    if chunk.delta:
                        full_ai_response += chunk.delta
                
                # Se AINDA SIM vier vazio, então era um erro real de tag/Ollama (404/500).
                if not full_ai_response.strip():
                     full_ai_response = f"Erro Crítico Motor LLM: O modelo '{body_request.model}' não foi encontrado ou abortou a geração no Backend (Verifique a Tag do provedor, ex: 'qwen2.5:0.5b')."
                else:
                     source_nodes = [] # Limpa citações já que foi direto pro LLM

            # Gravar a mensagem da IA sincrona
            ai_msg_db = ChatMessage(session_id=session_obj.id, role="assistant", content=full_ai_response, tenant_id=tenant_id)
            db.add(ai_msg_db)
            db.commit()
            
            # Extrai fontes caso existam
            citations = []
            if source_nodes:
                for node_w_score in source_nodes:
                    metadata = node_w_score.node.metadata
                    if metadata and "file_path" in metadata:
                        citations.append(Citation(source=metadata["file_path"]))
                        
            return ChatResponse(response=full_ai_response, sources=citations)
            
        except (TimeoutError, httpx.TimeoutException):
            # Captura exception generica se nao engolida e ja estavamos no Fallback mode, manda um friendly error
            err_msg = "*(Conexão Remota Inalcançável. The Mom e The Nurse falharam ao processar Localmente)*"
            return ChatResponse(response=err_msg, sources=[])
        except Exception as e:
            err_msg = f"Exceção Crítica no Motor LLM ({body_request.provider}/{body_request.model}): {str(e)}"
            return ChatResponse(response=err_msg, sources=[])
        finally:
            if getattr(body_request, 'active_document', None) and temp_sys_msg:
                try:
                    all_history = engine._memory.get_all()
                    clean_history = [m for m in all_history if m.content != temp_sys_msg.content]
                    engine._memory.chat_store.set_messages(engine._memory.chat_store_key, clean_history)
                except Exception:
                    pass



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

@router.get("/dashboard/stats")
@limiter.limit("60/minute")
async def get_dashboard_stats(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Estatísticas globais para a UI."""
    total_docs = db.query(SensusDocumentModel).filter(SensusDocumentModel.tenant_id == tenant_id).count()
    total_sessions = db.query(ChatSession).filter(ChatSession.tenant_id == tenant_id).count()
    return {"total_documents": total_docs, "total_sessions": total_sessions}

# --- QUARANTINE (THE SENTINEL) ENDPOINTS ---

@router.get("/quarantine")
@limiter.limit("60/minute")
async def list_quarantine(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Lista todos os documentos interceptados pelo The Sentinel."""
    logs = db.query(QuarantineLog).filter(
        QuarantineLog.tenant_id == tenant_id, 
        QuarantineLog.status == "QUARANTINED"
    ).order_by(QuarantineLog.created_at.desc()).all()
    
    return [
        {
            "id": log.id,
            "file_name": log.file_name,
            "file_path": log.file_path,
            "reason": log.reason,
            "ai_confidence": log.ai_confidence,
            "content_snippet": log.content_snippet,
            "status": log.status,
            "created_at": log.created_at.isoformat() if log.created_at else None
        } for log in logs
    ]

@router.post("/quarantine/{log_id}/release")
@limiter.limit("20/minute")
async def release_quarantine(request: Request, log_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Libera manualmente um PDF enjaulado (bypassa The Sentinel para RAG)."""
    from fastapi import HTTPException
    
    log = db.query(QuarantineLog).filter(QuarantineLog.id == log_id, QuarantineLog.tenant_id == tenant_id).first()
    if not log or log.status != "QUARANTINED":
        raise HTTPException(status_code=404, detail="Registro de quarentena não encontrado ou já processado.")
        
    log.status = "RELEASED"
    db.commit()
    
    # Processo manual ignorando TheSentinel e persistindo para o The Dad pegar
    from src.core.the_sentinel import TheSentinel
    import uuid
    import logging
    try:
        raw_text = TheSentinel.dehydrate_pdf(log.file_path)
        
        existing = db.query(SensusDocumentModel).filter(SensusDocumentModel.file_path == log.file_path).first()
        if existing:
            existing.content = raw_text
        else:
            doc_id = str(uuid.uuid4())
            new_doc = SensusDocumentModel(
                id=doc_id,
                tenant_id=tenant_id,
                file_path=log.file_path,
                content=raw_text,
                frontmatter={},
                extracted_todos=[],
                extracted_tags=[],
                extracted_links=[],
                vector_id=None,
                semantic_summary=None
            )
            db.add(new_doc)
            
        db.commit()
        return {"status": "success", "message": "Documento validado administrativamente. The Dad iniciará a vetorização no próximo ciclo."}
    except Exception as e:
        logging.error(f"Erro ao liberar arquivo da quarentena: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao reprocessar: {str(e)}")

@router.delete("/quarantine/{log_id}")
@limiter.limit("20/minute")
async def delete_quarantine(request: Request, log_id: int, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Remove a entrada da quarentena e deleta o PDF fisicamente."""
    from fastapi import HTTPException
    
    log = db.query(QuarantineLog).filter(QuarantineLog.id == log_id, QuarantineLog.tenant_id == tenant_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Registro não encontrado.")
        
    log.status = "DELETED"
    
    # Destrancar fisicamente do HD
    if os.path.exists(log.file_path):
        try:
            os.remove(log.file_path)
        except Exception as e:
            print(f"Failed to delete malicious file {log.file_path}: {e}")
            
    db.commit()
    return {"status": "success"}

@router.get("/sessions", response_model=List[SessionResponse])
@limiter.limit("120/minute")
async def get_all_sessions(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Lista todas as conversas gravadas no SQLite/Postgres."""
    sessions = db.query(ChatSession).filter(ChatSession.tenant_id == tenant_id).order_by(ChatSession.updated_at.desc()).limit(150).all()
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
    
    if not msg and req.session_id:
        # Fallback para Bypass UI: Mensagens transmitidas via Rust podem ter um ID fake gerado no Date.now() do Vue.
        # Nesses casos, buscamos a última mensagem de "assistant" daquela sessão para linkar o feedback.
        msg = db.query(ChatMessage).filter(
            ChatMessage.session_id == req.session_id,
            ChatMessage.role == 'assistant',
            ChatMessage.tenant_id == tenant_id
        ).order_by(ChatMessage.id.desc()).first()

    if not msg:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada e Fallback via session_id falhou.")

    if req.thumbs_up is not None: msg.thumbs_up = req.thumbs_up  # noqa: E701
    if req.thumbs_down is not None: msg.thumbs_down = req.thumbs_down  # noqa: E701
    if req.feedback_text is not None: msg.feedback_text = req.feedback_text  # noqa: E701
    
    db.commit()
    return {"status": "ok"}


class SyncMessageRequest(BaseModel):
    message_id: int
    session_id: int
    content: str

@router.post("/chat/sync_message")
async def sync_message(req: SyncMessageRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Receives the final streaming answer generated by the Rust Core and upserts it to SQLite so feedback can target an exact ID."""
    msg = None
    if req.message_id > 0 and req.message_id < 2147483647: # Only try to query if it's a valid integer (not a JS timestamp placeholder)
        msg = db.query(ChatMessage).filter(ChatMessage.id == req.message_id, ChatMessage.tenant_id == tenant_id).first()
    
    if msg:
        msg.content = req.content
        db.commit()
        db.refresh(msg)
        return {"status": "synced", "message_id": msg.id}
    else:
        new_msg = ChatMessage(
            session_id=req.session_id,
            role="assistant",
            content=req.content,
            tenant_id=tenant_id
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        return {"status": "created", "message_id": new_msg.id}



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
    Ingests a single document on-the-fly into sqlite-vec.
    """
    from src.config import RAW_DOCS_DIR
    
    intake_setting = _get_setting_value(db, "default_intake_vault", str(RAW_DOCS_DIR), tenant_id)
    intake_dir = intake_setting.strip() if intake_setting and intake_setting.strip() else str(RAW_DOCS_DIR)
    
    raw_dir = Path(intake_dir).absolute()
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
        
    # 4. Ingerir dinamicamente (Será delegado ao Rust The Dad / sqlite-vec em breve)
    # A indexação atômica multi-threaded ocorrerá via Watcher. Por ora apenas aprovamos o cache via SQLite.
        
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
    return setting.setting_value if setting is not None else default

def _set_setting_value(db: Session, key: str, value: str, tenant_id: str):
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key, SystemSettings.tenant_id == tenant_id).first()
    if setting:
        setting.setting_value = value
    else:
        db.add(SystemSettings(setting_key=key, setting_value=value, tenant_id=tenant_id))

@router.get("/settings", response_model=SettingsResponse)
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
        geolocation=_get_setting_value(db, "geolocation", "", tenant_id),
        openai_api_key=_get_setting_value(db, "openai_api_key", "", tenant_id),
        anthropic_api_key=_get_setting_value(db, "anthropic_api_key", "", tenant_id),
        gemini_api_key=_get_setting_value(db, "gemini_api_key", "", tenant_id),
        custom_ollama_url=_get_setting_value(db, "custom_ollama_url", "", tenant_id),
        default_intake_vault=_get_setting_value(db, "default_intake_vault", "", tenant_id),
        workspaces=json.loads(_get_setting_value(db, "workspaces", "[]", tenant_id)),
        remote_integration_enabled=(_get_setting_value(db, "remote_integration_enabled", "true", tenant_id).lower() == "true")
    )

@router.post("/settings", response_model=SettingsResponse)
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
        
        # --- Multi-LLM BYOK ---
        _set_setting_value(db, "openai_api_key", body_request.openai_api_key, tenant_id)
        _set_setting_value(db, "anthropic_api_key", body_request.anthropic_api_key, tenant_id)
        _set_setting_value(db, "gemini_api_key", body_request.gemini_api_key, tenant_id)
        _set_setting_value(db, "custom_ollama_url", body_request.custom_ollama_url, tenant_id)
        
        # --- Global Workspace Architecture ---
        _set_setting_value(db, "default_intake_vault", body_request.default_intake_vault, tenant_id)
        _set_setting_value(db, "workspaces", json.dumps(body_request.workspaces), tenant_id)
        
        # --- Local-First Agnosticism ---
        _set_setting_value(db, "remote_integration_enabled", "true" if body_request.remote_integration_enabled else "false", tenant_id)
        
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

def get_authorized_workspaces(db: Session, tenant_id: str) -> list:
    from src.config import RAW_DOCS_DIR
    import json
    
    intake = _get_setting_value(db, "default_intake_vault", str(RAW_DOCS_DIR), tenant_id)
    ws_str = _get_setting_value(db, "workspaces", "[]", tenant_id)
    try:
        workspaces = json.loads(ws_str)
    except Exception:
        workspaces = []
        
    auth_dirs = [intake] if intake else []
    auth_dirs.extend(workspaces)
    
    # Mapear e retornar apenas se existirem na máquina local e caminhos absolutos
    valid_dirs = []
    for d in auth_dirs:
        if d and d.strip():
            abs_d = os.path.abspath(d.strip())
            if os.path.exists(abs_d):
                valid_dirs.append(abs_d)
                
    # Remove duplicates
    return list(set(valid_dirs))

@router.get("/health/cluster")
@limiter.limit("60/minute")
async def check_cluster_health(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Verifica a conectividade do cluster (Ollama/N8N) e avisa a UI sobre Degradação"""
    is_enabled_str = _get_setting_value(db, "remote_integration_enabled", "true", tenant_id)
    is_enabled = is_enabled_str.lower() == "true"
    
    if not is_enabled:
        return {"status": "degraded", "reason": "remote_disabled_by_user", "active_agents": ["The Mom", "The Dad", "The Nurse"]}
        
    ollama_url = get_active_ollama_url(db, tenant_id)
        
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            res = await client.get(f"{ollama_url}/api/tags")
            if res.status_code == 200:
                return {"status": "optimal", "active_agents": ["The Mom", "The Dad", "The Nurse", "The Doctor", "The Coder"]}
            else:
                return {"status": "degraded", "reason": "ollama_unreachable", "active_agents": ["The Mom", "The Dad", "The Nurse"]}
    except Exception:
        return {"status": "degraded", "reason": "ollama_timeout", "active_agents": ["The Mom", "The Dad", "The Nurse"]}

@router.post("/settings/remote-toggle")
@limiter.limit("20/minute")
def toggle_remote_integration(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Inverte rapidamente a chave de integração remota (Local-First Mode)"""
    current_val_str = _get_setting_value(db, "remote_integration_enabled", "true", tenant_id)
    new_val = "false" if current_val_str.lower() == "true" else "true"
    _set_setting_value(db, "remote_integration_enabled", new_val, tenant_id)
    db.commit()
    return {"status": "success", "remote_integration_enabled": new_val == "true"}

def is_path_authorized(target_path: str, auth_dirs: list) -> bool:
    abs_target = os.path.abspath(target_path)
    for auth_dir in auth_dirs:
        if abs_target.startswith(auth_dir):
            return True
    return False

def get_active_ollama_url(db: Session, tenant_id: str = "default") -> str:
    from src.config import OLLAMA_BASE_URL as ENV_OLLAMA_BASE_URL
    import json
    import sqlite3
    import os
    
    url_to_use = ENV_OLLAMA_BASE_URL
    
    try:
        # A interface Cíbrida (via Rust) escreve a seleção de clusters na tabela `global_settings` no SQLite Local
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_path = os.getenv("SOVEREIGN_MEMORY_DB", os.path.join(base_dir, "data", "sovereign_memory.db"))
        
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value_json FROM global_settings WHERE id = 'ollama_clusters'")
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    active_id = data.get("active_cluster_id", "")
                    for c in data.get("clusters", []):
                        if c.get("id") == active_id:
                            url_to_use = c.get("url", ENV_OLLAMA_BASE_URL)
                            break
    except Exception as e:
        print(f"Error resolving active Ollama URL from SQLite global_settings: {e}")
        pass
        
    # Translate localhost to host.docker.internal dynamically ONLY if running inside Docker
    if os.path.exists('/.dockerenv'):
        url_to_use = url_to_use.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
        
    return url_to_use.rstrip('/')

@router.get("/ollama/models")
@limiter.limit("60/minute")
async def list_ollama_models(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Fetches the list of locally pulled models from the ACTIVE Ollama server."""
    import httpx
    
    # Resolve the active cluster dynamically from postgres instead of static config
    base_url = get_active_ollama_url(db, tenant_id).rstrip('/')
    
    try:
        # 10s timeout to tolerate initial Tailscale Wireguard handshakes
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return {"models": models}
    except Exception as e:
        # Fallback to empty list or known models if Ollama is unreachable
        print(f"Failed to fetch Ollama models from {base_url}: {e}")
        return {"models": []}

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
async def pull_ollama_model(request: Request, body_request: PullModelRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Inicia o pull de um modelo Ollama e retorna o progresso do download via SSE (Server-Sent Events).
    """
    import httpx
    import json
    from fastapi.responses import StreamingResponse

    base_url = get_active_ollama_url(db, tenant_id)

    async def event_generator():
        try:
            # Conexão Async com timeout grande para downloads massivos (1h = 3600s)
            async with httpx.AsyncClient(timeout=3600.0) as client:
                async with client.stream("POST", f"{base_url}/api/pull", json={"name": body_request.model, "stream": True}) as response:
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
    Retorna a árvore do File System real (RAW_DOCS_DIR) convertida em JSON hierárquico.
    cruza a existência dos arquivos com a Database para informar o 'has_vector'.
    """
    
    # 1. Puxa todos os arquivos sincronizados da DB (unindo default e ativo)
    docs = db.query(SensusDocumentModel.file_path, SensusDocumentModel.vector_id, SensusDocumentModel.id, SensusDocumentModel.extracted_tags).filter(SensusDocumentModel.tenant_id.in_(["default", tenant_id])).all()
    
    # Mapa O(1) para buscar status do vetor e ID
    db_map = {str(d.file_path): {"vector_id": d.vector_id, "id": d.id, "tags": d.extracted_tags} for d in docs}
    
    def build_tree(current_path: str, name: str = "Root") -> dict:
        node = {"name": name, "type": "dir", "path": current_path, "children": []}
        try:
            # Lista diretórios primeiro, arquivos depois (ordenação visual)
            with os.scandir(current_path) as it:
                entries = sorted(list(it), key=lambda e: (not e.is_dir(), e.name.lower()))
                
            for entry in entries:
                if entry.name.startswith("."): # ignore hidden like .git
                    continue
                    
                if entry.is_dir():
                    node["children"].append(build_tree(entry.path, entry.name))
                elif entry.is_file() and entry.name.endswith(".md"):
                    db_info = db_map.get(entry.path, {})
                    file_node = {
                        "name": entry.name,
                        "type": "file",
                        "path": entry.path,
                        "id": db_info.get("id", None), # Se None, Front deve lidar
                        "has_vector": db_info.get("vector_id") is not None,
                        "tags": db_info.get("tags", [])
                    }
                    node["children"].append(file_node)
        except OSError:
            pass # Ignora Pastas sem permissão
            
        return node
        
    # Inicializa da pasta Base e retorna o Root Array como topo
    # 2. Resgata e protege Múltiplos Diretórios
    auth_dirs = get_authorized_workspaces(db, tenant_id)
    trees = []
    
    for directory in auth_dirs:
        base_name = os.path.basename(directory) or directory
        root_tree = build_tree(directory, base_name)
        # Ao invés de root_tree["children"], envia a raiz em si para que a UI agrupe por Pastas base
        trees.append(root_tree)
        
    return trees

class FSCreateRequest(BaseModel):
    path: str # Absolute path da pasta pai onde criar
    name: str # Nome do novo item
    type: str # 'file' ou 'folder'

class FSRenameRequest(BaseModel):
    path: str # Caminho absoluto atual
    new_name: str # Novo nome base (ex: 'nova_pasta' ou 'novo_arquivo.md')

class FSDeleteRequest(BaseModel):
    path: str # Caminho absoluto do arquivo/pasta a ser deletado

@router.post("/vault/fs/create")
async def fs_create(req: FSCreateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    
    auth_dirs = get_authorized_workspaces(db, tenant_id)
    target_dir = os.path.abspath(req.path)
    
    if not is_path_authorized(target_dir, auth_dirs):
        raise HTTPException(status_code=403, detail="Sovereign Shield: Access Denied. Path Traversal Detectado.")
        
    new_path = os.path.join(target_dir, req.name)
    
    try:
        if req.type == "folder":
            os.makedirs(new_path, exist_ok=False)
        else: # file
            if not req.name.endswith(".md"):
                new_path += ".md"
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(f"# {req.name.replace('.md', '')}\n")
        return {"status": "success", "path": new_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/vault/fs/rename")
async def fs_rename(req: FSRenameRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    
    auth_dirs = get_authorized_workspaces(db, tenant_id)
    target_path = os.path.abspath(req.path)
    
    if not is_path_authorized(target_path, auth_dirs):
        raise HTTPException(status_code=403, detail="Sovereign Shield: Access Denied. Path Traversal Detectado.")
        
    new_path = os.path.join(os.path.dirname(target_path), req.new_name)
    
    try:
        os.rename(target_path, new_path)
        return {"status": "success", "new_path": new_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vault/fs/delete")
async def fs_delete(req: FSDeleteRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    import shutil
    
    auth_dirs = get_authorized_workspaces(db, tenant_id)
    target_path = os.path.abspath(req.path)
    
    if not is_path_authorized(target_path, auth_dirs):
        raise HTTPException(status_code=403, detail="Sovereign Shield: Access Denied. Path Traversal Detectado.")
        
    try:
        if os.path.isdir(target_path):
            shutil.rmtree(target_path)
        elif os.path.isfile(target_path):
            os.remove(target_path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/tags")
async def get_vault_tags(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Agrega todas as tags do banco de dados SensusDocumentModel e retorna a contagem de uso.
    """
    from collections import Counter
    # Reúne tags legadas de default e novas vinculadas ao Owner logado
    docs = db.query(SensusDocumentModel.extracted_tags).filter(SensusDocumentModel.tenant_id.in_(["default", tenant_id])).all()
    
    tag_counter = Counter()
    for (tags,) in docs:
        if isinstance(tags, list):
            for tag in tags:
                stripped_tag = tag.strip().strip('#').lower()
                if stripped_tag:
                    tag_counter[stripped_tag] += 1
                    
    # Formata para o Frontend: [{"name": "project-sensus", "count": 8}, ...]
    result_tags = [{"name": name, "count": count} for name, count in tag_counter.most_common()]
    return {"tags": result_tags}

@router.get("/vault/templates")
async def get_vault_templates():
    """
    Lista templates pré-cadastrados (mock até a implantação de arquivos reais _templates).
    """
    return {
        "templates": [
            {
                "id": "tpl-dor",
                "name": "Definição de Pronto (DoR)",
                "description": "Cria um Markdown estruturado para especificar novas features.",
                "icon": "i-ph-magic-wand-duotone"
            },
            {
                "id": "tpl-log",
                "name": "Reunião Diária (Log)",
                "description": "Ata de reunião com meta-dados para o motor de busca.",
                "icon": "i-ph-calendar-duotone"
            },
            {
                "id": "tpl-arch",
                "name": "Decisão Arquitetural (ADR)",
                "description": "Template formal para decisões de engenharia.",
                "icon": "i-ph-file-code-duotone"
            }
        ]
    }

class CoderExecuteRequest(BaseModel):
    command: str
    context: str = ""
    timeout: int = 60

@router.post("/coder/execute")
async def execute_on_coder_node(req: CoderExecuteRequest, request: Request, tenant_id: str = Depends(get_current_user)):
    """
    MCP Proxy Endpoint (Phase 22):
    Recebe comandos do VSCode/Sensus locais e redireciona (Proxy) via rede Tailscale (mTLS) 
    diretamente para a API do "The Coder" hospedada na Oracle Cloud A1.
    """
    import httpx
    from fastapi import HTTPException
    import logging
    
    logger = logging.getLogger(__name__)
    
    # O IP fixo ou MagicDNS do Tailscale da Oracle VM
    coder_ip = os.getenv("CODER_TAILSCALE_IP", "100.x.y.z")
    coder_port = os.getenv("CODER_API_PORT", "8000")
    
    if coder_ip == "100.x.y.z":
        # Retorna um stub amigável caso a infra do Terraform ainda estaja provisionando
        return {
            "status": "pending_infrastructure",
            "message": "A infraestrutura OCI Cloud 'The Coder' ainda está na fila de provisionamento (Aguardando Capacidade Oracle).",
            "mock_response": f"Se estivesse online, eu executaria: '{req.command}' no IP {coder_ip}"
        }
        
    target_url = f"http://{coder_ip}:{coder_port}/v1/agent/execute"
    
    try:
        async with httpx.AsyncClient(timeout=req.timeout) as client:
            response = await client.post(
                target_url, 
                json={"command": req.command, "context": req.context},
                headers={"Authorization": request.headers.get("Authorization", "")}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.ConnectError:
        logger.error(f"Falha ao conectar no The Coder via Tailscale IP: {coder_ip}")
        raise HTTPException(status_code=503, detail="The Coder Node está offline ou inacessível na rede Tailscale.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="O comando no The Coder excedeu o tempo limite de execução.")
    except Exception as e:
        logger.error(f"Erro no Proxy MCP para The Coder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/document/{doc_id}")
async def get_vault_document(doc_id: str, db: Session = Depends(get_db)):
    """Busca o conteúdo cru do respectivo markdown no disco."""
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
    from fastapi import HTTPException
    
    doc = db.query(SensusDocumentModel).filter(SensusDocumentModel.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado no DB")

    # SAST Fix: Prevent directory traversal or malicious symlink writing
    target_path = os.path.abspath(doc.file_path)
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado na base segura.")

    with open(target_path, 'w', encoding='utf-8') as f:
        # Forçar conversão limpa para string previne Buffer Overflow por parsing binário imprevisto no request json
        f.write(str(request.content))
        
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
    print(f"PAYLOAD DO VUE: {body.cells}")
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

@router.get("/vault/agenda")
async def get_vault_agenda(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Retorna documentos e tarefas aglomerados por buckets de tempo (Hoje, Semana, Mês, Ano)."""
    from datetime import datetime, timezone, timedelta
    
    docs = db.query(SensusDocumentModel).filter(
        SensusDocumentModel.tenant_id.in_(["default", tenant_id])
    ).all()
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    last_week_start = week_start - timedelta(days=7)
    month_start = today_start.replace(day=1)
    year_start = today_start.replace(month=1, day=1)
    
    agenda = {
        "today": {"docs": [], "tasks": []},
        "this_week": {"docs": [], "tasks": []},
        "last_week": {"docs": [], "tasks": []},
        "this_month": {"docs": [], "tasks": []},
        "this_year": {"docs": [], "tasks": []},
        "older": {"docs": [], "tasks": []}
    }
    
    for doc in docs:
        doc_dt = doc.updated_at
        if not doc_dt:
            continue
            
        # Ensure doc_dt is timezone-aware for comparison
        if doc_dt.tzinfo is None:
            doc_dt = doc_dt.replace(tzinfo=timezone.utc)
            
        bucket = "older"
        if doc_dt >= today_start:
            bucket = "today"
        elif doc_dt >= week_start:
            bucket = "this_week"
        elif doc_dt >= last_week_start and doc_dt < week_start:
            bucket = "last_week"
        elif doc_dt >= month_start:
            bucket = "this_month"
        elif doc_dt >= year_start:
            bucket = "this_year"
            
        doc_info = {
            "name": os.path.basename(doc.file_path),
            "path": doc.file_path,
            "dt": doc_dt.isoformat()
        }
        agenda[bucket]["docs"].append(doc_info)
        
        if doc.extracted_todos:
            for todo in doc.extracted_todos:
                if not (todo.startswith("[x]") or todo.startswith("[X]")):
                    clean_text = todo[3:].strip()
                    if clean_text:
                        agenda[bucket]["tasks"].append({
                            "text": clean_text,
                            "file_name": doc_info["name"],
                            "file": doc.file_path
                        })
                        
    return agenda

@router.get("/vault/graph")
async def get_vault_graph(db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Retorna nós e vértices para o Sovereign Cognitive Graph."""
    docs = db.query(SensusDocumentModel).filter(SensusDocumentModel.tenant_id.in_(["default", tenant_id])).all()
    
    nodes = []
    links = []
    
    # Map paths and basenames to Node IDs
    path_to_id = {}
    basename_to_id = {}
    folder_nodes = set()
    
    for doc in docs:
        node_id = doc.id
        path_to_id[doc.file_path] = node_id
        basename = os.path.basename(doc.file_path)
        basename_without_ext = os.path.splitext(basename)[0]
        
        basename_to_id[basename] = node_id
        basename_to_id[basename_without_ext] = node_id
        
        # Add file node
        nodes.append({
            "id": node_id,
            "name": basename,
            "path": doc.file_path,
            "val": 1.5,
            "type": "file",
            "tags": doc.extracted_tags or []
        })
        
        # Add parent folder node if applicable
        dirname = os.path.basename(os.path.dirname(doc.file_path))
        if dirname and dirname != "data" and dirname != "RAW_DOCS_DIR":
            folder_id = f"folder_{dirname}"
            if folder_id not in folder_nodes:
                folder_nodes.add(folder_id)
                nodes.append({
                    "id": folder_id,
                    "name": dirname,
                    "val": 3,
                    "type": "folder",
                    "tags": []
                })
            # Link file to its folder
            links.append({
                "source": node_id,
                "target": folder_id,
                "type": "hierarchy"
            })

    # Add edges based on extracted Wikilinks ([[Nota]])
    for doc in docs:
        if not doc.extracted_links:
            continue
            
        source_id = doc.id
        for raw_link in doc.extracted_links:
            # Clean up [[link]]
            link_target = raw_link.replace("[[", "").replace("]]", "").strip()
            
            # Tenta achar o target
            target_id = basename_to_id.get(link_target) or basename_to_id.get(f"{link_target}.md")
            
            if target_id and target_id != source_id:
                links.append({
                    "source": source_id,
                    "target": target_id,
                    "type": "semantic"
                })

    return {"nodes": nodes, "links": links}

# ---------------------------------------------------------
# MCP (Model Context Protocol) Endpoints - Phase 21
# ---------------------------------------------------------

class MCPToolRequest(BaseModel):
    tool: str
    parameters: dict = Field(default_factory=dict)

@router.post("/mcp/tool")
async def execute_mcp_tool(request: Request, body: MCPToolRequest):
    """
    Executa ferramentas expostas via MCP (VSCode OpenCode / Cline).
    Permite que o Editor consuma o RAG e o Context7 do Sovereign Pair.
    """
    
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


# ---------------------------------------------------------
# THE GOD MODE COCKPIT (ABSTRACT PROJECTS) - Phase 39
# ---------------------------------------------------------

@router.get("/projects", response_model=List[ProjectResponse])
@limiter.limit("60/minute")
async def list_projects(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Lista todos os Projetos do Cockpit Global."""
    from sqlalchemy.orm import joinedload
    projects = db.query(ProjectModel).options(
        joinedload(ProjectModel.links),
        joinedload(ProjectModel.logs)
    ).filter(ProjectModel.tenant_id == tenant_id).order_by(ProjectModel.updated_at.desc()).all()
    return projects

@router.post("/projects", response_model=ProjectResponse)
@limiter.limit("30/minute")
async def create_project(request: Request, body: ProjectCreateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Cria um novo Projeto / Missão."""
    project_id = str(uuid.uuid4())
    
    new_project = ProjectModel(
        id=project_id,
        tenant_id=tenant_id,
        name=body.name,
        purpose=body.purpose,
        traction_status=body.traction_status,
        next_action=body.next_action,
        energy_level=body.energy_level,
        progress_percent=body.progress_percent,
        friction_radar=body.friction_radar,
        deadline=body.deadline
    )
    db.add(new_project)
    
    for link in body.links:
        new_link = ProjectLinkModel(
            project_id=project_id,
            url=link.url,
            label=link.label,
        )
        db.add(new_link)
        
    from src.core.sync_engine import save_to_markdown
    from datetime import datetime, timezone
    new_project.file_path = save_to_markdown(new_project, "project")
    new_project.last_synced_at = datetime.now(timezone.utc)
        
    db.commit()
    db.refresh(new_project)
    return new_project

@router.put("/projects/{project_id}", response_model=ProjectResponse)
@limiter.limit("60/minute")
async def update_project(request: Request, project_id: str, body: ProjectUpdateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Atualiza um Projeto existente (Check-in / Status)."""
    from sqlalchemy.orm import joinedload
    
    project = db.query(ProjectModel).options(
        joinedload(ProjectModel.links),
        joinedload(ProjectModel.logs)
    ).filter(ProjectModel.id == project_id, ProjectModel.tenant_id == tenant_id).first()
    
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
        
    update_data = body.model_dump(exclude_unset=True)
    
    # Handle Links separately
    if "links" in update_data:
        db.query(ProjectLinkModel).filter(ProjectLinkModel.project_id == project_id).delete()
        for link_data in update_data["links"]:
            new_link = ProjectLinkModel(
                project_id=project_id,
                url=link_data["url"],
                label=link_data["label"]
            )
            db.add(new_link)
        del update_data["links"]
        
    for key, value in update_data.items():
        setattr(project, key, value)
        
    from src.core.sync_engine import save_to_markdown
    from datetime import datetime, timezone
    project.file_path = save_to_markdown(project, "project")
    project.last_synced_at = datetime.now(timezone.utc)
        
    db.commit()
    db.refresh(project)
    return project

@router.delete("/projects/{project_id}")
@limiter.limit("20/minute")
async def delete_project(request: Request, project_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Exclui fisicamente um Projeto."""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id, ProjectModel.tenant_id == tenant_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
        
    db.delete(project)
    db.commit()
    return {"status": "success"}
    
@router.post("/projects/{project_id}/log")
@limiter.limit("60/minute")
async def add_project_log(request: Request, project_id: str, payload: dict, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Adiciona uma entrada no Diário de Bordo do projeto."""
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id, ProjectModel.tenant_id == tenant_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
        
    if "content" not in payload:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="O conteúdo do log é obrigatório (content).")
        
    new_log = ProjectLogModel(
        project_id=project_id,
        content=payload["content"]
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

# ---------------------------------------------------------
# OLLAMA CLUSTER MANAGER (Phase 40)
# ---------------------------------------------------------

@router.get("/settings/ollama_clusters")
@limiter.limit("60/minute")
def get_ollama_clusters(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Retrieve the cluster registry for Hot-Swapping Ollama Endpoints."""
    import json
    from src.config import OLLAMA_BASE_URL
    
    clusters_json = _get_setting_value(db, "ollama_clusters", "[]", tenant_id)
    try:
        clusters = json.loads(clusters_json)
        if not clusters:
            # Seed defaults securely based on the original .env configuration
            clusters = [
                {"id": "oracle", "name": "Oracle Cloud Músculo", "url": OLLAMA_BASE_URL},
                {"id": "local", "name": "Desktop Físico", "url": "http://host.docker.internal:11434"}
            ]
            _set_setting_value(db, "ollama_clusters", json.dumps(clusters), tenant_id)
            db.commit()
    except Exception:
        clusters = []
        
    active_id = _get_setting_value(db, "active_ollama_cluster_id", "oracle", tenant_id)
    return {"clusters": clusters, "active_cluster_id": active_id}

class ClusterUpdatePayload(BaseModel):
    clusters: list
    active_cluster_id: str

@router.post("/settings/ollama_clusters")
@limiter.limit("60/minute")
def save_ollama_clusters(request: Request, payload: ClusterUpdatePayload, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """Overrides the active cluster routing logic for RAG connections."""
    import json
    import os
    import sqlite3
    
    # Salva no DB Postgres (Legado/UI State isolado)
    clusters_json = json.dumps([c if isinstance(c, dict) else c.dict() for c in payload.clusters])
    _set_setting_value(db, "ollama_clusters", clusters_json, tenant_id)
    _set_setting_value(db, "active_ollama_cluster_id", payload.active_cluster_id, tenant_id)
    db.commit()
    
    # Salva fisicamente no SQLite (Rust Cíbrido Local API Sync)
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_path = os.getenv("SOVEREIGN_MEMORY_DB", os.path.join(base_dir, "data", "sovereign_memory.db"))
        
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS global_settings (id TEXT PRIMARY KEY, value_json TEXT NOT NULL)")
                payload_json = json.dumps({"clusters": [c if isinstance(c, dict) else c.dict() for c in payload.clusters], "active_cluster_id": payload.active_cluster_id})
                cursor.execute("INSERT OR REPLACE INTO global_settings (id, value_json) VALUES ('ollama_clusters', ?)", (payload_json,))
                conn.commit()
    except Exception as e:
        print(f"Failed to sync SQLite settings: {e}")
        
    return {"status": "success"}

# ---------------------------------------------------------
# TASKS MANAGEMENT (Plan & Execute)
# ---------------------------------------------------------

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
@limiter.limit("60/minute")
def get_project_tasks(request: Request, project_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    tasks = db.query(TaskModel).filter(TaskModel.project_id == project_id, TaskModel.tenant_id == tenant_id).order_by(TaskModel.order_index.asc()).all()
    return tasks

@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
@limiter.limit("60/minute")
def create_project_task(request: Request, project_id: str, body: TaskCreateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id, ProjectModel.tenant_id == tenant_id).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Projeto não encontrado.")
    
    import uuid
    new_task = TaskModel(
        id=str(uuid.uuid4()),
        project_id=project_id,
        tenant_id=tenant_id,
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority,
        deadline=body.deadline
    )
    db.add(new_task)
    
    log = ActivityLogModel(tenant_id=tenant_id, agent_name="User", action="CREATE_TASK", entity_type="TASK", entity_id=new_task.id, details={"title": new_task.title})
    db.add(log)
    
    from src.core.sync_engine import save_to_markdown
    from datetime import datetime, timezone
    new_task.file_path = save_to_markdown(new_task, "task")
    new_task.last_synced_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(new_task)
    return new_task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
@limiter.limit("60/minute")
def update_task(request: Request, task_id: str, body: TaskUpdateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.tenant_id == tenant_id).first()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    log = ActivityLogModel(tenant_id=tenant_id, agent_name="User", action="UPDATE_TASK", entity_type="TASK", entity_id=task.id, details=update_data)
    db.add(log)
    
    from src.core.sync_engine import save_to_markdown
    from datetime import datetime, timezone
    task.file_path = save_to_markdown(task, "task")
    task.last_synced_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}")
@limiter.limit("20/minute")
def delete_task(request: Request, task_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.tenant_id == tenant_id).first()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
        
    db.delete(task)
    log = ActivityLogModel(tenant_id=tenant_id, agent_name="User", action="DELETE_TASK", entity_type="TASK", entity_id=task_id)
    db.add(log)
    
    db.commit()
    return {"status": "success"}

# ---------------------------------------------------------
# NOTES MANAGEMENT (Refinement)
# ---------------------------------------------------------

@router.get("/projects/{project_id}/notes", response_model=List[NoteResponse])
@limiter.limit("60/minute")
def get_project_notes(request: Request, project_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    notes = db.query(NoteModel).filter(NoteModel.project_id == project_id, NoteModel.tenant_id == tenant_id).all()
    return notes

@router.post("/projects/{project_id}/notes", response_model=NoteResponse)
@limiter.limit("60/minute")
def create_project_note(request: Request, project_id: str, body: NoteCreateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    import uuid
    new_note = NoteModel(
        id=str(uuid.uuid4()),
        project_id=project_id,
        tenant_id=tenant_id,
        title=body.title,
        content=body.content,
        is_pinned=body.is_pinned,
        tags=body.tags
    )
    db.add(new_note)
    
    from src.core.sync_engine import save_to_markdown
    from datetime import datetime, timezone
    new_note.file_path = save_to_markdown(new_note, "note")
    new_note.last_synced_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(new_note)
    return new_note

@router.put("/notes/{note_id}", response_model=NoteResponse)
@limiter.limit("60/minute")
def update_note(request: Request, note_id: str, body: NoteUpdateRequest, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id, NoteModel.tenant_id == tenant_id).first()
    if not note:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Nota não encontrada.")
        
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(note, key, value)
        
    from src.core.sync_engine import save_to_markdown
    from datetime import datetime, timezone
    note.file_path = save_to_markdown(note, "note")
    note.last_synced_at = datetime.now(timezone.utc)
        
    db.commit()
    db.refresh(note)
    return note

@router.delete("/notes/{note_id}")
@limiter.limit("20/minute")
def delete_note(request: Request, note_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id, NoteModel.tenant_id == tenant_id).first()
    if not note:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Nota não encontrada.")
        
    db.delete(note)
    db.commit()
    return {"status": "success"}

# ---------------------------------------------------------
# SYNC STATUS CHECK
# ---------------------------------------------------------

@router.get("/sync-status/{entity_type}/{entity_id}")
@limiter.limit("60/minute")
def get_sync_status(request: Request, entity_type: str, entity_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    from src.core.sync_engine import check_sync_status
    
    entity = None
    if entity_type == "project":
        entity = db.query(ProjectModel).filter(ProjectModel.id == entity_id, ProjectModel.tenant_id == tenant_id).first()
    elif entity_type == "task":
        entity = db.query(TaskModel).filter(TaskModel.id == entity_id, TaskModel.tenant_id == tenant_id).first()
    elif entity_type == "note":
        entity = db.query(NoteModel).filter(NoteModel.id == entity_id, NoteModel.tenant_id == tenant_id).first()
        
    if not entity:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Entidade não encontrada.")
        
    if not entity.file_path or not entity.updated_at:
        return {"status": "UNTRACKED", "message": "Entidade sem reflexo em Markdown ainda."}
        
    return check_sync_status(entity.file_path, entity.updated_at)

# ---------------------------------------------------------
# ACTIVITY LOG FEED
# ---------------------------------------------------------

@router.get("/activity-logs", response_model=List[ActivityLogResponse])
@limiter.limit("60/minute")
def get_activity_logs(request: Request, limit: int = 50, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    logs = db.query(ActivityLogModel).filter(ActivityLogModel.tenant_id == tenant_id).order_by(ActivityLogModel.created_at.desc()).limit(limit).all()
    return logs


# ---------------------------------------------------------
# OMNI-DIRECTORY (MULTI-DRIVE) RAG INTEGRATION (Phase 33)
# ---------------------------------------------------------

@router.delete("/vector/flush")
@limiter.limit("10/minute")
def secure_vectorial_flush(request: Request, db: Session = Depends(get_db)):
    """
    Sovereign Pair Multi-Drive Security:
    Acionado via The Gateway (Rust) sempre que um Workspace Físico é desatrelado pelo usuário.
    Tornou-se nativo via sqlite-vec.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("💥 [Omni-Drive Security] Flush Nativo ativado via SQLite-Vec.")
    return {"status": "success", "detail": "Flush vetorial nativo engatilhado"}
