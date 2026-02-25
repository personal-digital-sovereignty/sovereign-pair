import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Resolver PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .routes import router

app = FastAPI(
    title="Sovereign Pair RAG API",
    description="Interface REST para o núcleo RAG local-first.",
    version="1.0.0"
)

# CORS configuration para permitir plugins Obsidian e Web UIs futuramente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
