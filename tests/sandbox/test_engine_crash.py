import traceback
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Iniciando depuração de inicialização...")
try:
    print("Módulos importados. Tentando construir a Factory RAG localmente.")
    
    from src.agent import initialize_rag_tool
    _index, _ = initialize_rag_tool()
    print("Sucesso! O LlamaIndex iniciou.")
    print("Montando Chat Engine OLLAMA...")
    from src.engine_builder import build_chat_engine
    engine = build_chat_engine(_index, history=[])
    print("Chat Engine montado e respondendo. Não há erro de sintaxe ou conexão DB.")
except Exception:
    print("\nXXX ERRO FATAL XXX")
    traceback.print_exc()
