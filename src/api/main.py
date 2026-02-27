import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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

app = FastAPI(
    title="Sovereign Pair RAG API",
    description="Interface REST para o núcleo RAG local-first e híbrido de Nuvem.",
    version="3.0.0"
)

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

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "static", "favicon.png")
    return FileResponse(file_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
