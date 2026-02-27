import logging
import re
from typing import Any

# Regex patterns para capturar chaves sensíveis e tokens
SENSITIVE_PATTERNS = [
    # OpenAI, Anthropic, Mistral e chaves genéricas q começam com sk-
    re.compile(r"sk-[a-zA-Z0-9_-]{30,}"),
    
    # Google AI Studio / Gemini API Keys (são longos e alfanuméricos)
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    
    # Bearer Tokens / JWT genéricos
    re.compile(r"Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"),
    
    # Auth Tokens genéricos num payload JSON
    re.compile(r'("Authorization"\s*:\s*")[^"]+(")')
]

class RedactionFilter(logging.Filter):
    """
    Filtro de Logging de Segurança.
    Varre as mensagens de log buscando por padrões de Regex de chaves privadas (OpenAI, Gemini, JWTs).
    Substitui a chave exposta por [REDACTED] para prevenir vazamentos em logs de produção / Nuvem Pública.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Pular se o registro não tiver uma msg (ex. exceções corrompidas)
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            original_msg = record.msg
            for pattern in SENSITIVE_PATTERNS:
                # O caso especial é o Bearer/JSON Auth que usa grupos para não cortar a Keyword da string
                if pattern.pattern.startswith('("Auth'):
                    original_msg = pattern.sub(r'\1[REDACTED]\2', original_msg)
                else:
                    original_msg = pattern.sub("[REDACTED]", original_msg)
            
            # Atualiza a msg no registro do logger nativo do Python
            record.msg = original_msg
            
        # Se os args do logger tiverem strings sensíveis, precisamos ofuscá-los também
        if hasattr(record, 'args'):
            if isinstance(record.args, dict):
                new_args = {}
                for k, v in record.args.items():
                    if isinstance(v, str):
                        for pattern in SENSITIVE_PATTERNS:
                            if pattern.pattern.startswith('("Auth'):
                                v = pattern.sub(r'\1[REDACTED]\2', v)
                            else:
                                v = pattern.sub("[REDACTED]", v)
                    new_args[k] = v
                record.args = new_args
            elif isinstance(record.args, tuple):
                new_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        for pattern in SENSITIVE_PATTERNS:
                            if pattern.pattern.startswith('("Auth'):
                                arg = pattern.sub(r'\1[REDACTED]\2', arg)
                            else:
                                arg = pattern.sub("[REDACTED]", arg)
                    new_args.append(arg)
                record.args = tuple(new_args)

        return True

def setup_security_logging():
    """
    Injeta o RedactionFilter nos loggers chaves do projeto.
    Deve ser chamado na inicialização do main.py.
    """
    filter_instance = RedactionFilter()
    
    loggers_to_patch = [
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "llama_index",
        # root logger
        ""
    ]
    
    for name in loggers_to_patch:
        logger = logging.getLogger(name)
        # Previne duplicar o filtro se chamado multiplas vezes
        if not any(isinstance(f, RedactionFilter) for f in logger.filters):
            logger.addFilter(filter_instance)
