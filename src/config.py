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
from llama_index.core import Settings
from src.llm_factory import get_llm, get_embedding_model

# 1. Carregar variáveis de ambiente do arquivo .env local (sobrescreve o global para dev)
load_dotenv(override=True)

# 2. Carregar configuração global do SO (se existir e preencher o que faltar)
global_conf = Path(os.environ.get("SOVEREIGN_CONF", "~/.config/sovereign.conf")).expanduser()
if global_conf.exists():
    load_dotenv(global_conf)

# ============================================================================
# PATHS DO PROJETO (Absolutos)
# ============================================================================

# Diretório base do projeto (pasta pai de src/)
# Diretório base do projeto (pasta pai de src/)
# Tenta resolver via __file__ (confiável quando importado) ou sys.argv[0] (quando executado)
try:
    BASE_DIR = Path(__file__).parent.parent.resolve()
except NameError:
    BASE_DIR = Path.cwd()

# Diretório de dados base
DATA_DIR = BASE_DIR / "data"

# Diretório ChromaDB (sempre no projeto)
CHROMA_DIR = DATA_DIR / "chromadb"

# ============================================================================
# CAMINHOS DE INGESTÃO CUSTOMIZADOS
# ============================================================================

# Caminhos customizados (podem ser absolutos ou usar padrão)
VAULT_PATH_CUSTOM = os.getenv("VAULT_PATH", "").strip()
RAW_DOCS_PATHS_CUSTOM = os.getenv("RAW_DOCS_PATHS", "").strip()
FOLLOW_SYMLINKS = os.getenv("FOLLOW_SYMLINKS", "true").lower() == "true"

# Determinar caminhos finais
if VAULT_PATH_CUSTOM:
    VAULT_DIR = Path(VAULT_PATH_CUSTOM).expanduser().resolve()
else:
    VAULT_DIR = DATA_DIR / "vault"

if RAW_DOCS_PATHS_CUSTOM:
    # Suportar múltiplos caminhos separados por vírgula
    RAW_DOCS_DIRS = [
        Path(p.strip()).expanduser().resolve() 
        for p in RAW_DOCS_PATHS_CUSTOM.split(",")
        if p.strip()
    ]
else:
    RAW_DOCS_DIRS = [DATA_DIR / "raw_docs"]

# Manter RAW_DOCS_DIR para compatibilidade (primeiro caminho da lista)
RAW_DOCS_DIR = RAW_DOCS_DIRS[0]

# Extensões de arquivo permitidas para ingestão
ALLOWED_EXTENSIONS_STR = os.getenv(
    "ALLOWED_EXTENSIONS", 
    ".md,.pdf,.txt,.docx,.csv,.json,.html"
).strip()
ALLOWED_EXTENSIONS = [ext.strip() for ext in ALLOWED_EXTENSIONS_STR.split(",") if ext.strip()]


# ============================================================================
# CONFIGURAÇÕES DE CHUNKING
# ============================================================================

# Tamanho máximo de chunk para embeddings (em tokens, aprox 4 chars/token)
# Reduzido para 512 para aumentar a granularidade e precisão do RAG
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))

# Sobreposição entre chunks para manter contexto
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# ============================================================================
# CONFIGURAÇÕES DE HISTÓRICO DE INGESTÃO
# ============================================================================

# Arquivo de histórico para ingestão incremental
HISTORY_FILE = Path(os.getenv(
    "HISTORY_FILE",
    str(DATA_DIR / ".ingestion_history.json")
))

# Modo interativo (pergunta ao usuário sobre modo de ingestão)
INTERACTIVE_MODE = os.getenv("INTERACTIVE_MODE", "true").lower() == "true"


# ============================================================================
# CONFIGURAÇÕES DE PROVIDERS (API & LLM)
# ============================================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", LLM_PROVIDER).strip().lower()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "bge-m3")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "300.0"))

# Chaves de API de Terceiros (Cloud Providers)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


# ============================================================================
# IDENTIDADE E PERSONALIDADE (Multi-User)
# ============================================================================
OWNER_NAME = os.getenv("OWNER_NAME", "Jeferson").strip()
SOVEREIGN_NAME = os.getenv("SOVEREIGN_NAME", "Sovereign").strip()
OWNER_NICKNAME = os.getenv("OWNER_NICKNAME", OWNER_NAME).strip()
LANGUAGE = os.getenv("LANGUAGE", "Português do Brasil").strip()
GEOLOCATION = os.getenv("GEOLOCATION", "").strip()
OCCUPATION = os.getenv("OCCUPATION", "").strip()
ABOUT_USER = os.getenv("ABOUT_USER", "").strip()

# ============================================================================
# SEGURANÇA E CORS (Microserviços)
# ============================================================================
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,app://obsidian.md").strip()
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

# ============================================================================
# CONFIGURAÇÕES CHROMADB
# ============================================================================
# Nome da coleção no ChromaDB
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "sovereign_knowledge")

# Coleção para o Meta-RAG (Auto-conhecimento da arquitetura do Sovereign Pair)
CHROMA_SYSTEM_COLLECTION_NAME = os.getenv("CHROMA_SYSTEM_COLLECTION_NAME", "system_knowledge")


# ============================================================================
# CONFIGURAÇÕES DO AGENTE
# ============================================================================

ASSISTANT_PERSONA = os.getenv("ASSISTANT_PERSONA", "feminina") # Ex: feminina, masculina, neutra, robótica
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "true").lower() == "true"
MAX_WEB_SEARCH_RESULTS = int(os.getenv("MAX_WEB_SEARCH_RESULTS", "3"))

# ============================================================================
# INICIALIZAÇÃO DOS MODELOS (VIA FACTORY)
# ============================================================================

# Configuração do LLM para chat e geração de respostas
llm = get_llm(
    provider=LLM_PROVIDER,
    model=LLM_MODEL,
    temperature=0.1,
    request_timeout=REQUEST_TIMEOUT,
    base_url=OLLAMA_BASE_URL,
)

# Configuração do modelo de embeddings para vetorização de documentos
embed_model = get_embedding_model(
    provider=EMBEDDING_PROVIDER,
    model=EMBED_MODEL_NAME,
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
    Pula a validação se o provedor for diferente de Ollama.
    """
    if LLM_PROVIDER != "ollama" and EMBEDDING_PROVIDER != "ollama":
        return True
        
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
    Pula a verificação se o provedor não for Ollama.
    """
    if LLM_PROVIDER != "ollama" and EMBEDDING_PROVIDER != "ollama":
        return True, []
        
    import requests
    required_models = set()
    if LLM_PROVIDER == "ollama":
        required_models.add(LLM_MODEL)
    if EMBEDDING_PROVIDER == "ollama":
        required_models.add(EMBED_MODEL_NAME)
        
    if not required_models:
        return True, []
        
    missing_models = []
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            available_models = set()
            for model in models_data:
                full_name = model["name"]
                base_name = full_name.split(":")[0]
                available_models.add(full_name)
                available_models.add(base_name)
            
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
   Owner Name:    {OWNER_NAME}
   Verbose:       {AGENT_VERBOSE}
   Max Results:   {MAX_WEB_SEARCH_RESULTS}
"""


def validate_document_paths() -> tuple[bool, list[str]]:
    """
    Valida caminhos de documentos e links simbólicos.
    
    Returns:
        tuple: (todos_validos, lista_de_problemas)
    """
    problems = []
    
    # Validar VAULT_DIR
    if not VAULT_DIR.exists():
        problems.append(f"Vault path não existe: {VAULT_DIR}")
    elif VAULT_DIR.is_symlink() and not FOLLOW_SYMLINKS:
        problems.append(f"Vault é symlink mas FOLLOW_SYMLINKS=false: {VAULT_DIR}")
    elif VAULT_DIR.is_symlink():
        target = VAULT_DIR.resolve()
        if not target.exists():
            problems.append(f"Symlink quebrado em vault: {VAULT_DIR} -> {target}")
    
    # Validar RAW_DOCS_DIRS
    for i, path in enumerate(RAW_DOCS_DIRS, 1):
        if not path.exists():
            problems.append(f"Raw docs path {i} não existe: {path}")
        elif path.is_symlink() and not FOLLOW_SYMLINKS:
            problems.append(f"Path {i} é symlink mas FOLLOW_SYMLINKS=false: {path}")
        elif path.is_symlink():
            target = path.resolve()
            if not target.exists():
                problems.append(f"Symlink quebrado em raw docs {i}: {path} -> {target}")
    
    return len(problems) == 0, problems


def detect_obsidian_vault() -> Optional[Path]:
    """
    Tenta detectar Obsidian vault no sistema.
    
    Procura em locais comuns e verifica a presença do diretório .obsidian
    que marca um vault válido.
    
    Returns:
        Path: Caminho do primeiro vault encontrado ou None
    """
    vaults = find_obsidian_vaults()
    return vaults[0] if vaults else None


def find_obsidian_vaults(search_paths: Optional[list[Path]] = None) -> list[Path]:
    """
    Busca todos os Obsidian vaults no sistema.
    
    Args:
        search_paths: Lista de caminhos para buscar. Se None, usa locais comuns.
    
    Returns:
        list[Path]: Lista de caminhos de vaults encontrados
    """
    home = Path.home()
    vaults = []
    
    # Locais comuns para buscar
    if search_paths is None:
        search_paths = [
            home / "Documents",
            home / "Obsidian",
            home / "Notes",
            home / "Dropbox",
            home / "iCloudDrive",
            home,  # Buscar também no home
        ]
    
    # Buscar recursivamente (mas não muito profundo para evitar lentidão)
    max_depth = 3
    
    for base_path in search_paths:
        if not base_path.exists():
            continue
        
        try:
            # Buscar diretórios .obsidian (marca de vault)
            for obsidian_dir in base_path.rglob(".obsidian"):
                if obsidian_dir.is_dir():
                    vault_path = obsidian_dir.parent
                    
                    # Verificar profundidade
                    try:
                        depth = len(vault_path.relative_to(base_path).parts)
                        if depth <= max_depth:
                            if vault_path not in vaults:
                                vaults.append(vault_path)
                    except ValueError:
                        # Caminho não é relativo ao base_path
                        continue
        except (PermissionError, OSError):
            # Ignorar diretórios sem permissão
            continue
    
    return sorted(vaults)  # Ordenar para consistência


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