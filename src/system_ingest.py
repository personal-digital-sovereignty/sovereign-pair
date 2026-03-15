import logging
import json
import uuid
import struct
from sqlalchemy.sql import text
from llama_index.core import SimpleDirectoryReader
from src.config import get_embed_model, CHUNK_SIZE, CHUNK_OVERLAP, BASE_DIR

logger = logging.getLogger(__name__)

def ingest_system_knowledge():
    """
    Auto-ingestion pipeline for RAG (Phase 13 / Phase B).
    Reads the backend source code (.py) and documentation (.md), chunks it,
    embeds it using the local BGE-M3 model, and stores it in the native
    SQLite-vec tables ('sovereign_chunks' & 'vec0' virtual table) 
    using 'system' as tenant_id.
    """
    logger.info("=" * 60)
    logger.info("INICIANDO INGESTÃO DE SYSTEM KNOWLEDGE (RAG SQLite-Vec)")
    logger.info("=" * 60)

    try:
        from src.api.database import SessionLocal
        db = SessionLocal()
        
        # 0. Flush old system knowledge
        logger.info("Limpando índice RAG antigo...")
        db.execute(text("DELETE FROM sovereign_vectors WHERE chunk_id IN (SELECT chunk_id FROM sovereign_chunks WHERE tenant_id = 'system')"))
        db.execute(text("DELETE FROM sovereign_chunks WHERE tenant_id = 'system'"))
        db.commit()

        # 1. Obter arquivos de código e documentação
        src_dir = BASE_DIR / "src"
        docs_dir = BASE_DIR / "docs"
        
        target_files = []
        for f in ["README.md", "task.md", "CHANGELOG.md"]:
            p = BASE_DIR / f
            if p.exists():
                target_files.append(str(p))

        if src_dir.exists():
            for p in src_dir.rglob("*.py"):
                if "__pycache__" not in str(p) and not str(p).endswith("system_ingest.py"):
                    target_files.append(str(p))
                    
        if docs_dir.exists():
            for p in docs_dir.rglob("*.md"):
                target_files.append(str(p))

        if not target_files:
            logger.warning("Nenhum arquivo de sistema encontrado para indexar.")
            return

        logger.info(f"📂 Encontrados {len(target_files)} arquivos fonte de sistema.")

        # 2. Carregar e Chunkar
        documents = SimpleDirectoryReader(input_files=target_files).load_data()
        logger.info(f"📄 {len(documents)} documentos lidos fisicamente.")

        from llama_index.core.node_parser import SentenceSplitter
        parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        nodes = parser.get_nodes_from_documents(documents)
        logger.info(f"🧩 {len(nodes)} blocos de código/doc criados.")

        # 3. Gerar Embeddings e Inserir no SQLite-Vec (vec0)
        embed_model = get_embed_model()
        logger.info("⚡ Gerando vetores F32 e inserindo no SQLite Nativo...")

        for idx, node in enumerate(nodes):
            # Obter embedding síncrono
            embedding = embed_model.get_text_embedding(node.get_content())
            
            # Pacote para bytes little-endian F32, que o sqlite-vec Vec0 exige via binding
            embedding_bytes = struct.pack(f"{len(embedding)}f", *embedding)
            
            uuid_ref = str(uuid.uuid4())
            file_path = node.metadata.get("file_path", "unknown")
            metadata_json = json.dumps(node.metadata)
            
            # Inserir o Txt no Relacional
            res = db.execute(
                text("""
                INSERT INTO sovereign_chunks (uuid_reference, tenant_id, file_path, text_content, metadata_json)
                VALUES (:uuid, 'system', :fp, :tc, :meta)
                """),
                {
                    "uuid": uuid_ref,
                    "fp": file_path,
                    "tc": node.get_content(),
                    "meta": metadata_json
                }
            )
            chunk_id = res.lastrowid
            
            # Inserir o Vetor no vec0 (Virtual Table)
            try:
                db.execute(
                    text("INSERT INTO sovereign_vectors (chunk_id, embedding) VALUES (:cid, :emb)"),
                    {"cid": chunk_id, "emb": embedding_bytes}
                )
                db.commit() # <--- LIBERAR O DB LOCK AQUI
            except Exception as e:
                logger.error(f"Erro no vec0 insertion: {e}")
                db.rollback()
                
            if idx % 50 == 0 and idx > 0:
                logger.info(f"   ✓ Processados {idx}/{len(nodes)} blocos...")
                
        db.commit()
        db.close()
        
        logger.info("✅ Meta-RAG System Knowledge (SQLite-Vec) atualizado com sucesso!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Falha ao ingerir System Knowledge: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_system_knowledge()
