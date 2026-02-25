import sys
import os

# Necessário para localizar módulos da raiz (src)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import initialize_rag_tool
from engine_builder import build_chat_engine

# Intância Global
_chat_engine = None

def get_chat_engine():
    """
    Dependency Injection for FastAPI. Returns the globally instanced ContextChatEngine.
    This guarantees the RAG is only loaded into memory once for all endpoints.
    """
    global _chat_engine
    if _chat_engine is None:
        index, _ = initialize_rag_tool()
        _chat_engine = build_chat_engine(index)
    return _chat_engine
