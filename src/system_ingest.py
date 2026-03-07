import logging
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from config import CHROMA_DIR, CHROMA_SYSTEM_COLLECTION_NAME, get_embed_model, CHUNK_SIZE, CHUNK_OVERLAP, BASE_DIR

logger = logging.getLogger(__name__)

def ingest_system_knowledge():
    """
    Auto-ingestion pipeline for Meta-RAG (Phase 13).
    Reads the backend source code (.py) and documentation (.md) and stores it in a
    dedicated, isolated ChromaDB collection.
    """
    logger.info("=" * 60)
    logger.info("🧠 INICIANDO INGESTÃO DE SYSTEM KNOWLEDGE (Meta-RAG)")
    logger.info("=" * 60)

    try:
        # Define the paths to scan for system knowledge
        src_dir = BASE_DIR / "src"
        docs_dir = BASE_DIR / "docs"
        
        target_files = []
        
        # Add root project files
        for f in ["README.md", "task.md", "CHANGELOG.md"]:
            p = BASE_DIR / f
            if p.exists():
                target_files.append(str(p))

        # Add all Python files in src/
        if src_dir.exists():
            for p in src_dir.rglob("*.py"):
                # Ignore cached files
                if "__pycache__" not in str(p):
                    target_files.append(str(p))
                    
        # Add all Markdown files in docs/
        if docs_dir.exists():
            for p in docs_dir.rglob("*.md"):
                target_files.append(str(p))

        if not target_files:
            logger.warning("Nenhum arquivo de sistema encontrado para indexar.")
            return

        logger.info(f"📂 Encontrados {len(target_files)} arquivos fonte de sistema.")

        # Load documents
        documents = SimpleDirectoryReader(input_files=target_files).load_data()
        logger.info(f"📄 {len(documents)} documentos lidos fisicamente.")

        # Chunking Process
        from llama_index.core.node_parser import SentenceSplitter
        parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        nodes = parser.get_nodes_from_documents(documents)
        logger.info(f"🧩 {len(nodes)} blocos de código/doc criados.")

        # Setup isolated ChromaDB Collection
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        from config import get_chroma_client
        db = get_chroma_client()
        
        # Clear existing collection to ensure fresh code state on every boot
        try:
            db.delete_collection(CHROMA_SYSTEM_COLLECTION_NAME)
        except Exception:
            pass
            
        chroma_collection = db.get_or_create_collection(CHROMA_SYSTEM_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Generate embeddings and store
        logger.info("⚡ Gerando vetores espaciais para o Código Fonte...")
        VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            embed_model=get_embed_model(),
            show_progress=False
        )

        logger.info("✅ Meta-RAG System Knowledge atualizado com sucesso!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Falha ao ingerir System Knowledge: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_system_knowledge()
