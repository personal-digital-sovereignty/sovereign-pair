import logging
import sys
import os
from pathlib import Path

# Adicionar ../src ao path para importar config
sys.path.append(str(Path(__file__).parent.parent / "src"))

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding

# Importar configurações centralizadas
from config import (
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    EMBED_MODEL_NAME,
    OLLAMA_BASE_URL
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def debug_retrieval(query: str):
    print(f"\n🔎 Buscando por: '{query}'")
    print("-" * 50)
    
    try:
        # Configurar Embed Model
        embed_model = OllamaEmbedding(
            model_name=EMBED_MODEL_NAME,
            base_url=OLLAMA_BASE_URL,
        )
        
        # Conectar ao Chroma
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(CHROMA_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        
        # Carregar Index
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model
        )
        
        # Retriever
        retriever = index.as_retriever(similarity_top_k=5)
        nodes = retriever.retrieve(query)
        
        if not nodes:
            print("❌ Nenhum nó recuperado!")
            return
            
        print(f"✅ Recuperados {len(nodes)} nós:")
        for i, node in enumerate(nodes, 1):
            print(f"\n[Node {i}] Score: {node.score:.4f}")
            print(f"Arquivo: {node.metadata.get('file_path', 'N/A')}")
            print(f"--- Conteúdo Completo ({len(node.text)} chars) ---")
            print(node.text)
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    queries = ["Projeto Uninove", "ArchLinux", "Backup"]
    
    # Se passar argumento, usa ele
    if len(sys.argv) > 1:
        queries = [sys.argv[1]]
        
    for q in queries:
        debug_retrieval(q)
