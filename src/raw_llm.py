import json
import httpx
from typing import List, Dict, AsyncGenerator
from src.config import OLLAMA_BASE_URL, REQUEST_TIMEOUT

async def raw_astream_chat(
    provider: str, 
    model: str, 
    messages: List[Dict[str, str]], 
    api_keys: dict
) -> AsyncGenerator[str, None]:
    """
    Motor Barebone Httpx para Stream de Inferência, substituindo a caixa preta do LlamaIndex.
    Suporta Ollama local e provedores externos (OpenAI, Groq).
    """
    
    if provider == "ollama":
        base_url = api_keys.get("custom_ollama_url") or OLLAMA_BASE_URL
        endpoint = f"{base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            async with client.stream("POST", endpoint, json=payload) as response:
                response.raise_for_status()
                async for chunk in response.aiter_lines():
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue

    elif provider in ["openai", "groq"]:
        auth_key = api_keys.get(f"{provider}_api_key")
        if not auth_key:
            raise ValueError(f"Api key não encontrada para {provider}")

        # Roteamento de base_url
        if provider == "openai":
            base_url = "https://api.openai.com/v1"
        else:
            base_url = "https://api.groq.com/openai/v1"
            
        endpoint = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {auth_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[len("data: "):]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
                            
    else:
        # Fallback genérico para providers não mapeados na versão Raw
        raise NotImplementedError(f"O provedor Raw {provider} não foi mapeado no Core Barebone.")
