"""
Script de ingestão de documentos para o Sovereign Pair RAG.

Este módulo carrega documentos de múltiplas fontes, processa com chunking
inteligente (MarkdownNodeParser para .md), gera embeddings e armazena no 
ChromaDB para posterior recuperação pelo agente.
"""

import logging
import chromadb
from pathlib import Path
from typing import Optional
from tqdm import tqdm
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.vector_stores.chroma import ChromaVectorStore

# Importar configurações centralizadas
from config import (
    RAW_DOCS_DIR,
    RAW_DOCS_DIRS,
    VAULT_DIR,
    CHROMA_DIR,
    CHROMA_COLLECTION_NAME,
    FOLLOW_SYMLINKS,
    ALLOWED_EXTENSIONS,
    embed_model,
    validate_document_paths,
)

# Configurar logger
logger = logging.getLogger(__name__)


def load_documents_from_directory(
    directory: Path, 
    dir_name: str,
    follow_symlinks: bool = True
) -> list:
    """
    Carrega documentos de um diretório específico.
    
    Args:
        directory: Path do diretório a ser lido
        dir_name: Nome do diretório (para logging)
        follow_symlinks: Se deve seguir links simbólicos
        
    Returns:
        list: Lista de documentos carregados
    """
    documents = []
    
    if not directory.exists():
        logger.warning(f"⚠️  Diretório '{dir_name}' não encontrado: {directory}")
        return documents
    
    # Verificar se é symlink
    if directory.is_symlink():
        if not follow_symlinks:
            logger.warning(f"⚠️  Ignorando symlink '{dir_name}' (FOLLOW_SYMLINKS=false): {directory}")
            return documents
        
        target = directory.resolve()
        if not target.exists():
            logger.error(f"❌ Symlink quebrado '{dir_name}': {directory} -> {target}")
            return documents
        
        logger.info(f"🔗 Seguindo symlink '{dir_name}': {directory} -> {target}")
    
    # Verificar se há arquivos no diretório
    files = list(directory.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    
    if file_count == 0:
        logger.warning(f"⚠️  Diretório '{dir_name}' está vazio: {directory}")
        return documents
    
    try:
        logger.info(f"📂 Carregando documentos de '{dir_name}'...")
        docs = SimpleDirectoryReader(
            str(directory), 
            recursive=True,
            required_exts=ALLOWED_EXTENSIONS  # Filtro de extensões configurável
        ).load_data()
        documents.extend(docs)
        logger.info(f"   ✓ {len(docs)} documento(s) carregado(s) de '{dir_name}'")
    except Exception as e:
        logger.error(f"   ❌ Erro ao ler '{dir_name}': {e}")
    
    return documents


def ingest_data() -> Optional[VectorStoreIndex]:
    """
    Carrega documentos de caminhos configurados, gera embeddings e armazena no ChromaDB.
    
    O SimpleDirectoryReader suporta nativamente: .md, .pdf, .docx, .csv, .txt, etc.
    
    Returns:
        VectorStoreIndex: Índice criado com sucesso ou None em caso de erro
    """
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO INGESTÃO DE DOCUMENTOS")
    logger.info("=" * 70)
    
    # 1. Validar caminhos antes de começar
    logger.info("\n🔍 Validando caminhos de documentos...")
    paths_valid, problems = validate_document_paths()
    
    if not paths_valid:
        logger.error("❌ Problemas encontrados nos caminhos:")
        for problem in problems:
            logger.error(f"   - {problem}")
        logger.info("\n💡 Dica: Execute 'python setup.py' para configurar caminhos")
        logger.info("💡 Ou crie os diretórios manualmente:")
        logger.info(f"   mkdir -p {VAULT_DIR}")
        for path in RAW_DOCS_DIRS:
            logger.info(f"   mkdir -p {path}")
        return None
    
    logger.info("   ✓ Todos os caminhos são válidos")
    
    # 2. Carregar documentos de múltiplas fontes
    all_documents = []
    
    # Carregar de vault
    vault_docs = load_documents_from_directory(
        VAULT_DIR, 
        f"vault ({VAULT_DIR})",
        follow_symlinks=FOLLOW_SYMLINKS
    )
    all_documents.extend(vault_docs)
    
    # Carregar de raw_docs (pode ser múltiplos caminhos)
    for i, raw_docs_dir in enumerate(RAW_DOCS_DIRS, 1):
        dir_name = f"raw_docs_{i}" if len(RAW_DOCS_DIRS) > 1 else "raw_docs"
        raw_docs = load_documents_from_directory(
            raw_docs_dir,
            f"{dir_name} ({raw_docs_dir})",
            follow_symlinks=FOLLOW_SYMLINKS
        )
        all_documents.extend(raw_docs)
    
    # Verificar se há documentos para processar
    if not all_documents:
        logger.error("❌ Nenhum documento encontrado para indexar!")
        logger.info(f"   Verifique os diretórios:")
        logger.info(f"   - Vault: {VAULT_DIR}")
        for i, path in enumerate(RAW_DOCS_DIRS, 1):
            logger.info(f"   - Raw docs {i}: {path}")
        logger.info(f"\n💡 Extensões permitidas: {', '.join(ALLOWED_EXTENSIONS)}")
        return None
    
    logger.info(f"\n✅ Total: {len(all_documents)} documento(s) carregado(s)")
    
    # 2. Processar documentos com chunking inteligente
    logger.info("\n" + "=" * 70)
    logger.info("📋 Etapa 2/4: Processando documentos com chunking inteligente")
    logger.info("=" * 70)
    
    # Separar documentos Markdown dos demais
    markdown_docs = []
    other_docs = []
    
    for doc in all_documents:
        file_path = doc.metadata.get('file_path', '')
        if file_path.endswith('.md'):
            markdown_docs.append(doc)
        else:
            other_docs.append(doc)
    
    logger.info(f"   📝 Arquivos Markdown: {len(markdown_docs)}")
    logger.info(f"   📄 Outros formatos: {len(other_docs)}")
    
    # Processar Markdown com parser especializado
    all_nodes = []
    
    if markdown_docs:
        logger.info("\n   🧩 Processando Markdown com MarkdownNodeParser...")
        logger.info("      (Respeita cabeçalhos ## e blocos de código ```)")
        md_parser = MarkdownNodeParser()
        md_nodes = md_parser.get_nodes_from_documents(markdown_docs)
        all_nodes.extend(md_nodes)
        logger.info(f"      ✓ {len(md_nodes)} blocos semânticos criados")
    
    # Processar outros documentos
    if other_docs:
        logger.info(f"\n   📦 Processando {len(other_docs)} documentos não-Markdown...")
        from llama_index.core.node_parser import SimpleNodeParser
        simple_parser = SimpleNodeParser()
        other_nodes = simple_parser.get_nodes_from_documents(other_docs)
        all_nodes.extend(other_nodes)
        logger.info(f"      ✓ {len(other_nodes)} blocos criados")
    
    logger.info(f"\n   📊 Total de blocos (nodes): {len(all_nodes)}")
    if all_nodes:
        avg_size = sum(len(node.text) for node in all_nodes) // len(all_nodes)
        logger.info(f"   📏 Tamanho médio: {avg_size} caracteres")
    
    # 3. Inicializar ChromaDB
    logger.info("\n" + "=" * 70)
    logger.info("📋 Etapa 3/4: Configurando ChromaDB")
    logger.info("=" * 70)
    
    try:
        logger.info(f"   🗄️  Diretório: {CHROMA_DIR}")
        logger.info(f"   📦 Coleção: {CHROMA_COLLECTION_NAME}")
        
        # Garantir que o diretório existe
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        
        db = chromadb.PersistentClient(path=str(CHROMA_DIR))
        chroma_collection = db.get_or_create_collection(CHROMA_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        logger.info("   ✓ ChromaDB configurado com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
        logger.exception("Detalhes do erro:")
        return None
    
    # 4. Gerar embeddings e indexar
    logger.info("\n" + "=" * 70)
    logger.info("📋 Etapa 4/4: Gerando embeddings e indexando")
    logger.info("=" * 70)
    logger.info("   ⚡ Gerando coordenadas vetoriais com Ollama...")
    logger.info("   ☕ Isso pode levar alguns minutos. Pegue um café!")
    logger.info("")
    
    try:
        # Criar índice a partir dos nodes processados
        index = VectorStoreIndex(
            all_nodes,
            storage_context=storage_context,
            embed_model=embed_model,
            show_progress=True,
        )
        
        logger.info("")
        logger.info("   ✓ Embeddings gerados e salvos no ChromaDB")
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ INGESTÃO CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 70)
        logger.info(f"   📚 Documentos processados: {len(all_documents)}")
        logger.info(f"   🧩 Blocos (nodes) criados: {len(all_nodes)}")
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