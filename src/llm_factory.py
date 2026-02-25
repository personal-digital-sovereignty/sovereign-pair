import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

def get_llm(provider: str, model: str, temperature: float = 0.1, request_timeout: float = 300.0, **kwargs) -> Any:
    """
    Factory function para retornar a instância correta do LLM baseado no provedor.
    """
    provider = provider.lower()
    
    if provider == "ollama":
        from llama_index.llms.ollama import Ollama
        base_url = kwargs.get("base_url", "http://localhost:11434")
        return Ollama(
            model=model,
            request_timeout=request_timeout,
            base_url=base_url,
            temperature=temperature,
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
        base_url = kwargs.get("base_url", "http://localhost:11434")
        return OllamaEmbedding(
            model_name=model,
            base_url=base_url,
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

