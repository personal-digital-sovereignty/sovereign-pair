import sys
import os

# Necessário para localizar módulos da raiz (src)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import initialize_rag_tool
from engine_builder import build_chat_engine

from fastapi import Request, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import ChatMessage
from .auth import get_current_user
import json

# Intância Global do Índice (Para não recarregar o ChromaDB a cada request)
_index = None

async def get_chat_engine(request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_current_user)):
    """
    Dependency Injection for FastAPI. 
    Lê o `session_id` do Request e remonta o ContextChatEngine dinamicamente
    com a memória extraída do SQLite caso exista.
    """
    global _index
    if _index is None:
        _index, _ = initialize_rag_tool()
        
    provider = None
    model_name = None
    history_dicts = []
    
    # É perfeitamente seguro chamar await request.body() em uma dependência do FastAPI.
    # O framework guarda os bytes em cache para que o Pydantic parser lide bem depois.
    try:
        body_bytes = await request.body()
        body = json.loads(body_bytes) if body_bytes else {}
        session_id = body.get("session_id")
        provider = body.get("provider")
        model_name = body.get("model")
        
        if session_id:
            historical_msgs = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id,
                ChatMessage.tenant_id == tenant_id
            ).order_by(ChatMessage.created_at.asc()).all()
            history_dicts = [{"role": msg.role, "content": msg.content} for msg in historical_msgs]
    except Exception:
        pass
        
    return build_chat_engine(_index, history=history_dicts, provider=provider, model_name=model_name, tenant_id=tenant_id)
