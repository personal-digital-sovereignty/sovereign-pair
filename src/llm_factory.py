import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

def _get_setting(key: str, default: str) -> str:
    """Helper local para buscar configurações no DB de forma síncrona dentro do Worker."""
    try:
        from src.api.database import SessionLocal
        from src.api.models import SystemSettings
        db = SessionLocal()
        setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()
        val = setting.setting_value if setting and setting.setting_value else default
        db.close()
        return val
    except Exception:
        return default

import time

_health_cache = {}
_HEALTH_CACHE_TTL = 30.0

def _check_url_health(url: str) -> bool:
    """Valida rapidamente se o Host Remoto está vivo enviando HEAD na porta, cacheando resultado."""
    now = time.time()
    if url in _health_cache:
        status, ts = _health_cache[url]
        if now - ts < _HEALTH_CACHE_TTL:
            return status

    import requests
    try:
        # Ping agressivo de 2 segundos. Se não responder, o nó não serve pro RAG Fast-Path.
        r = requests.get(f"{url}/api/tags", timeout=2.0)
        is_up = r.status_code == 200
    except Exception:
        is_up = False
        
    _health_cache[url] = (is_up, now)
    
    if not is_up:
        logger.warning(f"⚠️  Nó remoto {url} está OFFLINE (Timeout > 2s). Forçando bypass.")
        
    return is_up

def _get_active_ollama_url() -> str:
    """Resolve a URL do cluster ativo em tempo real no banco, aplicando TTL Healthcheck."""
    from src.config import OLLAMA_BASE_URL
    import json
    
    active_id = _get_setting("active_ollama_cluster_id", "")
    if not active_id:
        return OLLAMA_BASE_URL
        
    clusters_json = _get_setting("ollama_clusters", "[]")
    try:
        clusters = json.loads(clusters_json)
        for c in clusters:
            if c.get("id") == active_id:
                url = c.get("url", OLLAMA_BASE_URL)
                
                # Se for diferente do nó local padrāo, valida a saúde pra não travar a UI toda
                if url and url != OLLAMA_BASE_URL and not _check_url_health(url):
                    return OLLAMA_BASE_URL
                return url
    except Exception:
        pass
        
    return OLLAMA_BASE_URL

def get_llm(provider: str, model: str, temperature: float = 0.1, request_timeout: float = 900.0, **kwargs) -> Any:
    """
    Factory function para retornar a instância correta do LLM baseado no provedor.
    Se existir configuração no DB SystemSettings (Fase 9), ele vai sobrepor os argumentos aqui recebidos do config.py.
    """
    # Overrides via Banco de Dados
    provider = _get_setting("llm_provider", provider).lower()
    model = _get_setting("llm_model", model)
    try:
        temp_str = _get_setting("temperature", str(temperature))
        temperature = float(temp_str)
    except ValueError:
        pass
    
    if provider == "ollama":
        from llama_index.llms.ollama import Ollama
        from src.config import OLLAMA_NUM_CTX, OLLAMA_BASE_URL
        
        # Override the static base URL if a Custom Cluster was selected
        dynamic_url = _get_active_ollama_url()
        # Se o url dinamico do DB for diferente do hardcoded passadocomo kwarg (OLLAMA_BASE_URL), a gente força o dinâmico
        base_url = dynamic_url if dynamic_url != OLLAMA_BASE_URL else kwargs.get("base_url", dynamic_url)
        base_url = base_url.rstrip('/')
        
        return Ollama(
            model=model,
            request_timeout=request_timeout,
            base_url=base_url,
            temperature=temperature,
            context_window=OLLAMA_NUM_CTX,
            additional_kwargs={
                # Forçar o "Zero Cold Boot" mantendo o modelo em VRAM ativamente 
                # (ou -1 se for permanente local-only host, mas 24h previne leaks residuais longo prazo)
                "keep_alive": "24h",
                # Mapeamento estrito das options direto para o llama.cpp via Ollama REST
                "options": {
                    "num_ctx": OLLAMA_NUM_CTX,
                    "num_keep": 24, # Isola as instruções de base do system prompt
                }
            },
        )
    elif provider == "openai":
        from llama_index.llms.openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY não configurada no .env")
        return OpenAI(
            model=model.replace("openai/", ""), # Permitir nomenclaturas com prefixo opcional
            temperature=temperature,
            api_key=api_key,
            request_timeout=request_timeout,
        )
    elif provider == "anthropic":
        from llama_index.llms.anthropic import Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY não configurada no .env")
        return Anthropic(
            model=model.replace("anthropic/", ""),
            temperature=temperature,
            api_key=api_key,
            timeout=request_timeout,
        )
    elif provider == "groq":
        from llama_index.llms.groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY não configurada no .env")
        return Groq(
            model=model.replace("groq/", ""),
            temperature=temperature,
            api_key=api_key,
            request_timeout=request_timeout,
        )
    elif provider == "gemini":
        raise ValueError("O provedor Gemini foi temporariamente blindado e removido do Sovereign Pair para permitir a mitigação de Nível Crítico (CVE do pacote Pillow >= 12.1.1).")
    else:
        raise ValueError(f"Provedor LLM não suportado: {provider}")

def get_embedding_model(provider: str, model: str, **kwargs) -> Any:
    """
    Factory function para retornar a instância correta do modelo de Embeddings baseado no provedor.
    """
    provider = provider.lower()
    
    if provider == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding
        from src.config import OLLAMA_BASE_URL
        
        dynamic_url = _get_active_ollama_url()
        base_url = dynamic_url if dynamic_url != OLLAMA_BASE_URL else kwargs.get("base_url", dynamic_url)
        base_url = base_url.rstrip('/')
        
        logger.info(f"🧩 [DEBUG] get_embedding_model: resolving '{model}' | default={OLLAMA_BASE_URL} | DB={dynamic_url} -> FINAL_URL={base_url}")
        
        return OllamaEmbedding(
            model_name=model,
            base_url=base_url,
            ollama_additional_kwargs={"keep_alive": "24h"}
        )
    elif provider == "openai":
        from llama_index.embeddings.openai import OpenAIEmbedding
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY não configurada.")
        return OpenAIEmbedding(
            model=model.replace("openai/", ""),
            api_key=api_key,
        )
    else:
        # Padrão ou HuggingFace local
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        try:
            return HuggingFaceEmbedding(model_name=model)
        except Exception as e:
            logger.error(f"Erro ao carregar HuggingFaceEmbedding ({model}): {e}")
            raise ValueError(f"Provedor de Embeddings não suportado: {provider}")

