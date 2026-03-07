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

def _get_active_ollama_url() -> str:
    """Resolve a URL do cluster ativo em tempo real no banco, ignorando o .env."""
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
                return c.get("url", OLLAMA_BASE_URL)
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
        from src.config import OLLAMA_NUM_CTX
        
        # Override the static base URL if a Custom Cluster was selected
        dynamic_url = _get_active_ollama_url()
        base_url = kwargs.get("base_url", dynamic_url).rstrip('/')
        
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
        from llama_index.llms.gemini import Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY não configurada no .env")
        return Gemini(
            model=model.replace("gemini/", ""),
            temperature=temperature,
            api_key=api_key,
        )
    else:
        raise ValueError(f"Provedor LLM não suportado: {provider}")

def get_embedding_model(provider: str, model: str, **kwargs) -> Any:
    """
    Factory function para retornar a instância correta do modelo de Embeddings baseado no provedor.
    """
    provider = provider.lower()
    
    if provider == "ollama":
        from llama_index.embeddings.ollama import OllamaEmbedding
        dynamic_url = _get_active_ollama_url()
        base_url = kwargs.get("base_url", dynamic_url).rstrip('/')
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

