import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from config import embed_model

def ingest_data():
    print("Carregando documentos...")
    # O SimpleDirectoryReader lê nativamente .md, .pdf, .docx, .csv
    documents = SimpleDirectoryReader("../data/raw_docs", recursive=True).load_data()
    documents += SimpleDirectoryReader("../data/vault", recursive=True).load_data()

    print("Inicializando ChromaDB...")
    db = chromadb.PersistentClient(path="../data/chromadb")
    chroma_collection = db.get_or_create_collection("sovereign_knowledge")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Gerando embeddings e indexando (isso pode levar um tempo na primeira vez)...")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context, 
        embed_model=embed_model
    )
    print("Indexação concluída!")

if __name__ == "__main__":
    ingest_data()