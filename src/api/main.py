import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Resolver PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .routes import router
from .database import engine, Base
from . import models

# Cria o banquinho de dados e as tabelas CADA VEZ que o app iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sovereign Pair RAG API",
    description="Interface REST para o núcleo RAG local-first.",
    version="1.0.0"
)

# CORS configuration para permitir plugins Obsidian e Web UIs futuramente
from src.config import ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Depends
from .auth import router as auth_router, get_current_user
app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
app.include_router(router, prefix="/v1", dependencies=[Depends(get_current_user)])

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "static", "favicon.png")
    return FileResponse(file_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
