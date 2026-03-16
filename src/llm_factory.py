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

import time  # noqa: E402

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
    """Resolve a URL do cluster ativo em tempo real no banco SQLite (Rust Core), aplicando TTL Healthcheck."""
    from src.config import OLLAMA_BASE_URL
    import json
    import sqlite3
    
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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
                            url = c.get("url", OLLAMA_BASE_URL)
                            if url and os.path.exists('/.dockerenv'):
                                url = url.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
                            # Se for diferente do nó local padrāo, valida a saúde
                            if url and url != OLLAMA_BASE_URL and not _check_url_health(url):
                                return OLLAMA_BASE_URL
                            return url.rstrip('/')
    except Exception as e:
        logger.error(f"Erro ao ler ollama_clusters do SQLite: {e}")
        pass
        
    return OLLAMA_BASE_URL.rstrip('/')

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
    else:
        raise ValueError(f"Provedor LLM não suportado (apenas ollama disponível nesta build soberana): {provider}")

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
    else:
        # Padrão ou HuggingFace local
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        try:
            return HuggingFaceEmbedding(model_name=model)
        except Exception as e:
            logger.error(f"Erro ao carregar HuggingFaceEmbedding ({model}): {e}")
            raise ValueError(f"Provedor de Embeddings não suportado: {provider}")

