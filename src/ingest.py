"""
Script de ingestão de documentos para o Sovereign Pair RAG.

Este módulo carrega documentos de múltiplas fontes, gera embeddings
e armazena no ChromaDB para posterior recuperação pelo agente.
"""

import logging
import chromadb
from pathlib import Path
from typing import Optional
from tqdm import tqdm
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

# Importar configurações centralizadas
from config import (
    RAW_DOCS_DIR,
    VAULT_DIR,
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    embed_model,
)

# Configurar logger
logger = logging.getLogger(__name__)


def load_documents_from_directory(directory: Path, dir_name: str) -> list:
    """
    Carrega documentos de um diretório específico.
    
    Args:
        directory: Path do diretório a ser lido
        dir_name: Nome do diretório (para logging)
        
    Returns:
        list: Lista de documentos carregados
    """
    documents = []
    
    if not directory.exists():
        logger.warning(f"⚠️  Diretório '{dir_name}' não encontrado: {directory}")
        return documents
    
    # Verificar se há arquivos no diretório
    files = list(directory.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    
    if file_count == 0:
        logger.warning(f"⚠️  Diretório '{dir_name}' está vazio: {directory}")
        return documents
    
    try:
        logger.info(f"📂 Carregando documentos de '{dir_name}'...")
        docs = SimpleDirectoryReader(str(directory), recursive=True).load_data()
        documents.extend(docs)
        logger.info(f"   ✓ {len(docs)} documento(s) carregado(s) de '{dir_name}'")
    except Exception as e:
        logger.error(f"   ❌ Erro ao ler '{dir_name}': {e}")
    
    return documents


def ingest_data() -> Optional[VectorStoreIndex]:
    """
    Carrega documentos de raw_docs e vault, gera embeddings e armazena no ChromaDB.
    
    O SimpleDirectoryReader suporta nativamente: .md, .pdf, .docx, .csv, .txt, etc.
    
    Returns:
        VectorStoreIndex: Índice criado com sucesso ou None em caso de erro
    """
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO INGESTÃO DE DOCUMENTOS")
    logger.info("=" * 70)
    
    # 1. Carregar documentos de múltiplas fontes
    all_documents = []
    
    # Carregar de raw_docs
    raw_docs = load_documents_from_directory(RAW_DOCS_DIR, "raw_docs")
    all_documents.extend(raw_docs)
    
    # Carregar de vault
    vault_docs = load_documents_from_directory(VAULT_DIR, "vault")
    all_documents.extend(vault_docs)
    
    # Verificar se há documentos para processar
    if not all_documents:
        logger.error("❌ Nenhum documento encontrado para indexar!")
        logger.info(f"   Verifique os diretórios:")
        logger.info(f"   - {RAW_DOCS_DIR}")
        logger.info(f"   - {VAULT_DIR}")
        return None
    
    logger.info(f"\n📊 Total: {len(all_documents)} documento(s) carregado(s)")
    
    # 2. Inicializar ChromaDB
    try:
        logger.info(f"\n🗄️  Inicializando ChromaDB em: {CHROMA_DIR}")
        
        # Garantir que o diretório existe
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        
        db = chromadb.PersistentClient(path=str(CHROMA_DIR))
        chroma_collection = db.get_or_create_collection(CHROMA_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        logger.info(f"   ✓ Coleção '{CHROMA_COLLECTION_NAME}' pronta")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
        return None
    
    # 3. Gerar embeddings e indexar
    try:
        logger.info("\n🧠 Gerando embeddings e indexando...")
        logger.info("   (isso pode levar alguns minutos dependendo da quantidade de documentos)")
        
        # Criar índice com progress bar
        index = VectorStoreIndex.from_documents(
            all_documents,
            storage_context=storage_context,
            show_progress=True,
        )
        
        logger.info("\n✅ Indexação concluída com sucesso!")
        logger.info(f"   📊 Documentos indexados: {len(all_documents)}")
        logger.info(f"   💾 Armazenado em: {CHROMA_DIR}")
        logger.info("=" * 70)
        
        return index
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante indexação: {e}")
        logger.exception("Detalhes do erro:")
        return None


def main():
    """Função principal para execução do script."""
    try:
        index = ingest_data()
        
        if index is None:
            logger.error("\n⚠️  Ingestão falhou. Verifique os logs acima.")
            exit(1)
        else:
            logger.info("\n🎉 Ingestão concluída com sucesso!")
            logger.info("   Você pode agora executar o agente para fazer queries.")
            exit(0)
            
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Ingestão cancelada pelo usuário.")
        exit(130)
    except Exception as e:
        logger.error(f"\n❌ Erro inesperado: {e}")
        logger.exception("Detalhes:")
        exit(1)


if __name__ == "__main__":
    main()