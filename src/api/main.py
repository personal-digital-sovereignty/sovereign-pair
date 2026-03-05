import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
# Resolver PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .routes import router
from .database import engine
from . import models

# Cria o banquinho de dados e as tabelas CADA VEZ que o app iniciar
models.Base.metadata.create_all(bind=engine)

# Injetar Filtro de Segurança Obscurecedor de Logs (Reminência de API Keys)
from .security_logger import setup_security_logging  # noqa: E402
setup_security_logging()

# Configurar Rate Limiter (Usa memória RAM temporariamente até termos Redis na Nuvem)
# get_remote_address pega o IP do cliente (ou o IP real via cabeçalhos X-Forwarded-For se atrás de Nginx/Tailscale)
limiter = Limiter(key_func=get_remote_address)

def auto_pull_ollama_models():
    """Baixa automaticamente os modelos definidos no config.py se eles faltarem no contêiner do Ollama."""
    import logging
    from src.config import validate_ollama_models, OLLAMA_BASE_URL
    import time
    from ollama import Client
    
    # Aguarda o Ollama subir caso estejam inicializando juntos
    time.sleep(10)
    
    try:
        is_valid, missing = validate_ollama_models()
        if not is_valid and missing:
            logging.info(f"🚀 Modelos ausentes no Ollama em rede isolada detectados: {missing}. Iniciando Auto-Pull via SDK...")
            
            client = Client(host=OLLAMA_BASE_URL)
            for model in missing:
                logging.info(f"📥 Baixando pesos do modelo {model}... (Isso pode demorar dependendo da banda larga e do tamanho do modelo)")
                try:
                    # O Client.pull bloqueia de forma segura até terminar
                    client.pull(model)
                    logging.info(f"✅ Modelo {model} foi baixado e ingerido no cache do Ollama com sucesso!")
                except Exception as pull_err:
                    logging.error(f"❌ Erro ao conectar no endpoint pull do {model}: {pull_err}")
    except Exception as e:
        logging.error(f"❌ Erro na rotina de Auto-Pull nativa do Ollama: {e}")

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Startup: Disparar Ingestão do Meta-RAG (System Knowledge)
    from src.system_ingest import ingest_system_knowledge
    import threading
    
    # Roda em thread separada para não bloquear o boot da API
    ingest_thread = threading.Thread(target=ingest_system_knowledge, daemon=True)
    ingest_thread.start()
    
    # Auto-Pull dos Ollama Models (Thread separada para não bloquear e lidar com gigabytes de I/O)
    pull_thread = threading.Thread(target=auto_pull_ollama_models, daemon=True)
    pull_thread.start()
    
    # Iniciar "The Mom" (Predictor/Watcher silêncioso no background)
    from src.core.the_mom import VaultWatcher
    from src.config import VAULT_DIR
    from src.api.database import SessionLocal
    from src.api.routes import get_authorized_workspaces
    import os
    
    # Garantir que a pasta Vault exista
    os.makedirs(VAULT_DIR, exist_ok=True)
    
    # 1. Obter Workspaces configurados pelo usuario na DB
    db = SessionLocal()
    try:
        from src.api.models import SystemSettings
        active_tenants = db.query(SystemSettings.tenant_id).distinct().all()
        workspaces = []
        
        for (t_id,) in active_tenants:
            workspaces.extend(get_authorized_workspaces(db, t_id))
            
        workspaces = list(set(workspaces))
        
        if str(VAULT_DIR) not in workspaces:
            workspaces.append(str(VAULT_DIR))
    except Exception as e:
        import logging
        logging.error(f"Erro ao buscar workspaces no DB: {e}")
        workspaces = [str(VAULT_DIR)]
    finally:
        db.close()
    
    # The Mom vai escutar dezenas de diretórios e parsear qualquer Markdown
    mom_watcher = VaultWatcher(tenant_id="default", vault_paths=workspaces)
    mom_watcher.start()
    
    # Iniciar "The Dad" (SLM Context Pre-Fetcher & Vectorizer)
    from src.core.the_dad import TheDadWorker
    dad_worker = TheDadWorker(check_interval_seconds=15)
    dad_worker.start()
    
    yield
    
    # Shutdown logic
    mom_watcher.stop()
    dad_worker.stop()
    # Auto-Pull dos Ollama Models (Thread separada para não bloquear e lidar com gigabytes de I/O)
    pull_thread = threading.Thread(target=auto_pull_ollama_models, daemon=True)
    pull_thread.start()
    
    yield
    # Shutdown logic (opcional)

app = FastAPI(
    title="Sovereign Pair RAG API",
    description="Interface REST para o núcleo RAG local-first e híbrido de Nuvem.",
    version="3.0.0",
    lifespan=app_lifespan
)

# --- MCP (Model Context Protocol) Server Integration ---
from src.api.mcp_server import mount_mcp_server
mount_mcp_server(app)

# Adicionar Rate Limiter ao estado global do app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- SEGURANÇA: MIDDLEWARES DE NUVEM (Phase 8) ---

# 1. HSTS (HTTP Strict Transport Security) - Proteção contra MitM
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Força navegadores e clientes a só usarem HTTPS por 1 ano (31536000 segundos)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Previne Clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # Previne MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# CORS configuration para permitir plugins Obsidian e Web UIs futuramente
from src.config import ALLOWED_ORIGINS  # noqa: E402

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Depends  # noqa: E402
from .auth import router as auth_router, get_current_user  # noqa: E402
app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(router, prefix="/v1", dependencies=[Depends(get_current_user)])

# CISO GOTCHA: Route Amputation & B2B Stripping
from src.config import SENSUS_MODE
if SENSUS_MODE != "enterprise":
    import logging
    logging.info("[B2B Route Amputation] SENSUS_MODE is standard. Registering Student/Productivity Routes.")
    from .routes_student import router as student_router
    app.include_router(student_router, prefix="/v1/student", tags=["Student Productivity"])
else:
    import logging
    logging.warning("[B2B Route Amputation] 🛡️ SENSUS_MODE=enterprise is ACTIVE. Student capabilities (Pomodoro, etc) are strictly AMPUTATED from OpenAPI.")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "static", "favicon.png")
    return FileResponse(file_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
