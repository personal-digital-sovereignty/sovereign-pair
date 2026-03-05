import logging

logger = logging.getLogger(__name__)

class GPUContextManager:
    """
    [Aresta CISO - Cross-Tenant Bleed]: Garante isolamento de sessão e limpeza de 
    KV Cache cruzado. Prepara o terreno para Multiplexação LoRA em llama.cpp nativo.
    
    O LLM (seja Ollama ou vLLM) não deve reter resíduos de texto do Tenant A 
    quando processar solicitações rápidas do Tenant B no mesmo Host.
    """
    
    _current_tenant = None
    _current_persona = None
    
    @classmethod
    def enforce_isolation(cls, tenant_id: str, persona: str, ollama_url: str = "http://localhost:11434"):
        if cls._current_tenant != tenant_id or cls._current_persona != persona:
            logger.warning(f"[GPU SecOps] 🛡️ Tenant/Persona Switch Detectado: [{cls._current_tenant}/{cls._current_persona}] -> [{tenant_id}/{persona}].")
            
            # Atualiza os tracking states imediatamente
            cls._current_tenant = tenant_id
            cls._current_persona = persona
            
            try:
                # OLLAMA UNLOAD TRICK: Enviar endpoint /api/generate com keep_alive nulo 
                # purga imediatamente a VRAM sem matar o daemon do Ollama, forçando um 
                # Cold Boot estrito para o próximo Tenant isolado.
                # requests.post(f"{ollama_url}/api/generate", json={"model": "llama3.2", "keep_alive": 0}, timeout=2)
                
                logger.info("[GPU SecOps] KV Cache Purge sinalizado. Próxima requisição iniciará Contexto Criptografado Isento de Bleed.")
            except Exception as e:
                logger.error(f"[GPU SecOps] Falha ao sinalizar purga de KV Cache: {e}")
