"""
Configurações centralizadas do projeto Sovereign Pair RAG.

Este módulo contém todas as configurações, paths e inicializações
necessárias para o funcionamento do sistema RAG local.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Settings

# Carregar variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# ============================================================================
# PATHS DO PROJETO (Absolutos)
# ============================================================================

# Diretório base do projeto (pasta pai de src/)
BASE_DIR = Path(__file__).parent.parent.resolve()

# Diretórios de dados
DATA_DIR = BASE_DIR / "data"
RAW_DOCS_DIR = DATA_DIR / "raw_docs"
VAULT_DIR = DATA_DIR / "vault"
CHROMA_DIR = DATA_DIR / "chromadb"

# ============================================================================
# CONFIGURAÇÕES OLLAMA
# ============================================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "nomic-embed-text")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "120.0"))

# ============================================================================
# CONFIGURAÇÕES CHROMADB
# ============================================================================

CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "sovereign_knowledge")

# ============================================================================
# CONFIGURAÇÕES DO AGENTE
# ============================================================================

USER_NAME = os.getenv("USER_NAME", "Jeferson")
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "true").lower() == "true"
MAX_WEB_SEARCH_RESULTS = int(os.getenv("MAX_WEB_SEARCH_RESULTS", "3"))

# ============================================================================
# INICIALIZAÇÃO DOS MODELOS
# ============================================================================

# Configuração do LLM para chat e geração de respostas
llm = Ollama(
    model=LLM_MODEL,
    request_timeout=REQUEST_TIMEOUT,
    base_url=OLLAMA_BASE_URL,
    temperature=0.1,  # Temperatura baixa para respostas mais precisas em RAG
)

# Configuração do modelo de embeddings para vetorização de documentos
embed_model = OllamaEmbedding(
    model_name=EMBED_MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
)

# ============================================================================
# CONFIGURAÇÃO GLOBAL DO LLAMAINDEX
# ============================================================================

# Configurar Settings globalmente para que todos os componentes usem
Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def validate_ollama_connection() -> bool:
    """
    Valida se o Ollama está acessível e rodando.
    
    Returns:
        bool: True se conectado com sucesso, False caso contrário
    """
    import requests
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Erro ao conectar com Ollama: {e}")
        return False


def validate_ollama_models() -> tuple[bool, list[str]]:
    """
    Verifica se os modelos necessários estão disponíveis no Ollama.
    
    Returns:
        tuple: (todos_modelos_disponiveis, lista_de_modelos_faltantes)
    """
    import requests
    
    required_models = {LLM_MODEL, EMBED_MODEL_NAME}
    missing_models = []
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            available_models = {model["name"].split(":")[0] for model in response.json().get("models", [])}
            missing_models = [m for m in required_models if m not in available_models]
            return len(missing_models) == 0, missing_models
        else:
            return False, list(required_models)
    except Exception as e:
        logging.error(f"Erro ao verificar modelos Ollama: {e}")
        return False, list(required_models)


def ensure_directories() -> None:
    """
    Garante que todos os diretórios necessários existam.
    Cria os diretórios se não existirem.
    """
    directories = [DATA_DIR, RAW_DOCS_DIR, VAULT_DIR, CHROMA_DIR]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Diretório verificado/criado: {directory}")


def get_config_summary() -> str:
    """
    Retorna um resumo das configurações atuais.
    
    Returns:
        str: String formatada com as configurações principais
    """
    return f"""
╔══════════════════════════════════════════════════════════════╗
║           SOVEREIGN PAIR - CONFIGURAÇÕES                     ║
╚══════════════════════════════════════════════════════════════╝

📁 Paths:
   BASE_DIR:      {BASE_DIR}
   DATA_DIR:      {DATA_DIR}
   CHROMA_DIR:    {CHROMA_DIR}

🤖 Ollama:
   URL:           {OLLAMA_BASE_URL}
   LLM Model:     {LLM_MODEL}
   Embed Model:   {EMBED_MODEL_NAME}
   Timeout:       {REQUEST_TIMEOUT}s

💾 ChromaDB:
   Collection:    {CHROMA_COLLECTION_NAME}

👤 Agente:
   User Name:     {USER_NAME}
   Verbose:       {AGENT_VERBOSE}
   Max Results:   {MAX_WEB_SEARCH_RESULTS}
"""


# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Garantir que diretórios existam
ensure_directories()

# Log de inicialização
logger = logging.getLogger(__name__)
logger.info("Configurações carregadas com sucesso")
logger.debug(get_config_summary())