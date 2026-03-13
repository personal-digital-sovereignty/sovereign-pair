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

# 1. Carregar variáveis de ambiente do arquivo .env local (Não sobrescreve envs já injetados, ex: pela CLI)
load_dotenv(override=False)

# 2. Carregar configuração global do SO (se existir e preencher o que faltar)
global_conf = Path(os.environ.get("SOVEREIGN_CONF", "~/.config/sovereign.conf")).expanduser()
if global_conf.exists():
    load_dotenv(global_conf)

# ============================================================================
# TUNELAMENTO - MALHA MESH (EDGE VS CLOUD)
# ============================================================================
OCI_MESH_URL = os.getenv("OCI_MESH_URL", "").strip().rstrip("/")
OCI_MESH_TOKEN = os.getenv("OCI_MESH_TOKEN", "").strip()

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


# ============================================================================
# CAMINHOS DE INGESTÃO CUSTOMIZADOS
# ============================================================================

# Caminhos customizados (podem ser absolutos ou usar padrão)
VAULT_PATH_CUSTOM = os.getenv("VAULT_PATH", "").strip()
RAW_DOCS_PATHS_CUSTOM = os.getenv("RAW_DOCS_PATHS", "").strip()
FOLLOW_SYMLINKS = os.getenv("FOLLOW_SYMLINKS", "true").lower() == "true"

if VAULT_PATH_CUSTOM and not os.path.exists('/.dockerenv'):
    VAULT_DIR = Path(VAULT_PATH_CUSTOM).expanduser().resolve()
else:
    VAULT_DIR = DATA_DIR / "vault"

if RAW_DOCS_PATHS_CUSTOM and not os.path.exists('/.dockerenv'):
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
# LLM & EMBEDDING CONFIGURATION
# ============================================================================

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", LLM_PROVIDER).strip().lower()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()

# Correção Automática de Hostname se rodando Nativo (Fora do Docker)
# Se o .env tiver "http://ollama:11434" mas rodarmos via CLI nativa, o request falharia silenciosamente no LlamaIndex ("Empty Response").
if "ollama:11434" in OLLAMA_BASE_URL and not os.path.exists('/.dockerenv'):
    OLLAMA_BASE_URL = OLLAMA_BASE_URL.replace("ollama:11434", "localhost:11434")

# LlamaIndex env vars global behavior
os.environ["OLLAMA_BASE_URL"] = OLLAMA_BASE_URL
# Fallback local para CLI e scripts rodando na máquina hospedeira
if "http://ollama:" in OLLAMA_BASE_URL and not os.getenv("CHROMA_HOST"):
    OLLAMA_BASE_URL = OLLAMA_BASE_URL.replace("http://ollama:", "http://localhost:")
    
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL", "bge-m3")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "300.0"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))

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
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,app://sensusvault.local").strip()
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]

# ============================================================================
# B2B ENTERPRISE FLAGS (CISO Gotchas)
# ============================================================================
# If 'enterprise', student-tier features (e.g. Pomodoro routes) are strictly amputated from FastAPI Swagger.
SENSUS_MODE = os.getenv("SENSUS_MODE", "standard").strip().lower()



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
def get_default_llm():
    from src.llm_factory import get_llm
    from src.llm_factory import _get_active_ollama_url
    return get_llm(
        provider=LLM_PROVIDER,
        model=LLM_MODEL,
        temperature=0.1,
        request_timeout=REQUEST_TIMEOUT,
        base_url=_get_active_ollama_url() or OLLAMA_BASE_URL,
    )

def get_embed_model():
    """Retorna o Embed Model despachado para a Nuvem Mapeada dinamicamente."""
    # Importar get_embedding_model aqui para carregamento dinâmico, se necessário
    from src.llm_factory import get_embedding_model
    from src.llm_factory import _get_active_ollama_url
    return get_embedding_model(
        provider=EMBEDDING_PROVIDER,
        model=EMBED_MODEL_NAME,
        base_url=_get_active_ollama_url() or OLLAMA_BASE_URL,
    )

# ============================================================================
# CONFIGURAÇÃO GLOBAL DO LLAMAINDEX
# ============================================================================

# O LlamaIndex prefere instâncias nos Settings. Deixaremos 'none' explicitamente 
# configurado para OBRIGAR injeção local de dependência dinâmica nos componentes.
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def validate_ollama_connection() -> bool:
    """Verifica se o serviço principal do Ollama (do cluster ativo) está acessível."""
    if LLM_PROVIDER != "ollama":
        return True
    import requests
    try:
        from src.llm_factory import _get_active_ollama_url
        dynamic_url = _get_active_ollama_url()
        response = requests.get(f"{dynamic_url}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Erro ao conectar com Ollama no cluster ativo: {e}")
        return False

def validate_ollama_models() -> tuple[bool, list]:
    """Valida se os modelos requeridos estão instalados no Ollama atual configurado."""
    if LLM_PROVIDER != "ollama":
        return True, []
        
    import requests
    required_models = set([LLM_MODEL, EMBED_MODEL_NAME])
    
    try:
        from src.llm_factory import _get_active_ollama_url
        dynamic_url = _get_active_ollama_url()
        response = requests.get(f"{dynamic_url}/api/tags", timeout=5)
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
        import logging
        logging.error(f"Erro ao verificar modelos Ollama no cluster ativo: {e}")
        return False, list(required_models)
def ensure_directories() -> None:
    """
    Garante que todos os diretórios necessários existam.
    Cria os diretórios se não existirem.
    """
    directories = [DATA_DIR, RAW_DOCS_DIR, VAULT_DIR]
    
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

🤖 Ollama:
🤖 Ollama:
   URL:           {OLLAMA_BASE_URL}
   LLM Model:     {LLM_MODEL}
   Embed Model:   {EMBED_MODEL_NAME}
   Timeout:       {REQUEST_TIMEOUT}s

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


def detect_sensus_vault() -> Optional[Path]:
    """
    Tenta detectar Sensus Vault no sistema.
    """
    return VAULT_DIR

def find_sensus_vaults(search_paths: Optional[list[Path]] = None) -> list[Path]:
    """
    Busca vaults no sistema.
    """
    return [VAULT_DIR]


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