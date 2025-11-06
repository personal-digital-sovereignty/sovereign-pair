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
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    HISTORY_FILE,
    INTERACTIVE_MODE,
    embed_model,
    validate_document_paths,
)

# Importar módulos de ingestão incremental (Fase 1 + 2)
from history import IngestionHistory
from diff import detect_new_files, detect_modified_files, detect_deleted_files
from interactive import show_changes_summary, prompt_ingestion_mode
from hash_utils import compute_file_hash
from cleanup import remove_obsolete_chunks

# Configurar logger
logger = logging.getLogger(__name__)


def load_documents_from_directory(
    directory: Path, 
    dir_name: str,
    follow_symlinks: bool = True
) -> list:
    """
    Carrega documentos de um diretório, seguindo symlinks de diretórios se configurado.
    
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
    
    # Coletar todos os caminhos a processar (resolvendo symlinks)
    paths_to_process = []
    visited_paths = set()  # Evitar loops infinitos
    
    # Escanear diretório em busca de arquivos, diretórios e symlinks
    try:
        for item in directory.iterdir():
            # Verificar se é symlink
            if item.is_symlink():
                if not follow_symlinks:
                    logger.warning(f"⚠️  Ignorando symlink '{item.name}' (FOLLOW_SYMLINKS=false)")
                    continue
                
                # Resolver symlink
                try:
                    target = item.resolve(strict=True)
                except (OSError, RuntimeError) as e:
                    logger.error(f"❌ Symlink quebrado '{item.name}': {item} -> erro: {e}")
                    continue
                
                # Evitar loops infinitos
                if target in visited_paths:
                    logger.warning(f"⚠️  Symlink circular detectado, ignorando: {item.name}")
                    continue
                
                visited_paths.add(target)
                
                if target.is_dir():
                    logger.info(f"🔗 Seguindo symlink de diretório: {item.name} -> {target}")
                    paths_to_process.append(target)
                elif target.is_file():
                    logger.info(f"🔗 Seguindo symlink de arquivo: {item.name} -> {target}")
                    if target.suffix in ALLOWED_EXTENSIONS:
                        paths_to_process.append(target)
            
            # Diretório ou arquivo real (não symlink)
            elif item.is_dir():
                if item not in visited_paths:
                    visited_paths.add(item)
                    paths_to_process.append(item)
            elif item.is_file():
                if item.suffix in ALLOWED_EXTENSIONS:
                    paths_to_process.append(item)
    
    except PermissionError as e:
        logger.error(f"❌ Sem permissão para ler '{dir_name}': {e}")
        return documents
    
    # Verificar se há caminhos para processar
    if not paths_to_process:
        logger.warning(f"⚠️  Diretório '{dir_name}' está vazio ou sem arquivos compatíveis: {directory}")
        return documents
    
    # Processar cada caminho com SimpleDirectoryReader
    logger.info(f"📂 Carregando documentos de '{dir_name}'...")
    
    for path in paths_to_process:
        try:
            if path.is_file():
                # Processar arquivo individual
                docs = SimpleDirectoryReader(
                    input_files=[str(path)]
                ).load_data()
                documents.extend(docs)
            elif path.is_dir():
                # Processar diretório recursivamente
                docs = SimpleDirectoryReader(
                    str(path),
                    recursive=True,
                    required_exts=ALLOWED_EXTENSIONS
                ).load_data()
                documents.extend(docs)
                logger.info(f"   ✓ {len(docs)} documento(s) de '{path.name}/'")
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar '{path.name}': {e}")
    
    if documents:
        logger.info(f"   ✓ Total: {len(documents)} documento(s) carregado(s) de '{dir_name}'")
    
    return documents


def scan_all_files() -> set[Path]:
    """
    Escaneia todos os arquivos nos diretórios configurados.
    
    Retorna conjunto de Paths absolutos de todos os arquivos encontrados,
    sem carregá-los. Usado para detecção de mudanças na ingestão incremental.
    
    Returns:
        Conjunto de Paths absolutos de todos os arquivos
    """
    all_files = set()
    
    # Escanear vault
    if VAULT_DIR.exists():
        for ext in ALLOWED_EXTENSIONS:
            all_files.update(VAULT_DIR.rglob(f"*{ext}"))
    
    # Escanear raw_docs (pode ser múltiplos caminhos)
    for raw_docs_dir in RAW_DOCS_DIRS:
        if raw_docs_dir.exists():
            for ext in ALLOWED_EXTENSIONS:
                all_files.update(raw_docs_dir.rglob(f"*{ext}"))
    
    # Resolver symlinks se configurado
    if FOLLOW_SYMLINKS:
        resolved_files = set()
        for file_path in all_files:
            try:
                resolved = file_path.resolve(strict=True)
                resolved_files.add(resolved)
            except (OSError, RuntimeError):
                logger.warning(f"⚠️  Ignorando arquivo com erro: {file_path}")
        return resolved_files
    
    return all_files


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


def scan_all_files() -> set[Path]:
    """
    Escaneia todos os arquivos nos diretórios configurados.
    
    Retorna conjunto de Paths absolutos de todos os arquivos encontrados,
    sem carregá-los. Usado para detecção de mudanças na ingestão incremental.
    
    Returns:
        Conjunto de Paths absolutos de todos os arquivos
    """
    all_files = set()
    
    # Escanear vault
    if VAULT_DIR.exists():
        for ext in ALLOWED_EXTENSIONS:
            all_files.update(VAULT_DIR.rglob(f"*{ext}"))
    
    # Escanear raw_docs (pode ser múltiplos caminhos)
    for raw_docs_dir in RAW_DOCS_DIRS:
        if raw_docs_dir.exists():
            for ext in ALLOWED_EXTENSIONS:
                all_files.update(raw_docs_dir.rglob(f"*{ext}"))
    
    # Resolver symlinks se configurado
    if FOLLOW_SYMLINKS:
        resolved_files = set()
        for file_path in all_files:
            try:
                resolved = file_path.resolve(strict=True)
                resolved_files.add(resolved)
            except (OSError, RuntimeError):
                logger.warning(f"⚠️  Ignorando arquivo com erro: {file_path}")
        return resolved_files
    
    return all_files


def load_specific_files(file_paths: set[Path]) -> list:
    """
    Carrega apenas arquivos específicos (modo incremental).
    
    Args:
        file_paths: Conjunto de Paths de arquivos a carregar
        
    Returns:
        Lista de documentos carregados
    """
    from llama_index.core import SimpleDirectoryReader
    
    documents = []
    
    logger.info(f"\n📂 Carregando {len(file_paths)} arquivo(s) específico(s)...")
    
    for file_path in tqdm(file_paths, desc="Carregando"):
        try:
            docs = SimpleDirectoryReader(
                input_files=[str(file_path)]
            ).load_data()
            documents.extend(docs)
            logger.debug(f"   ✓ {file_path.name}: {len(docs)} documento(s)")
        except Exception as e:
            logger.error(f"   ❌ Erro ao carregar {file_path.name}: {e}")
    
    logger.info(f"✅ {len(documents)} documento(s) carregado(s)")
    return documents


def update_history_with_hashes(
    index: Optional[VectorStoreIndex],
    processed_files: set[Path],
    deleted_files: set[Path],
    history: 'IngestionHistory'
) -> None:
    """
    Atualiza histórico com hashes SHA256 dos arquivos processados.
    
    Args:
        index: Índice criado (pode ser None)
        processed_files: Arquivos que foram processados
        deleted_files: Arquivos que foram deletados
        history: Instância do histórico
    """
    logger.info("\n💾 Atualizando histórico...")
    
    # Coletar dados dos arquivos processados
    files_data = {}
    
    # Contar chunks por arquivo
    if index and hasattr(index, 'docstore'):
        for node_id, node in index.docstore.docs.items():
            file_path_str = node.metadata.get('file_path', '')
            if file_path_str:
                file_path = Path(file_path_str)
                if file_path in processed_files:
                    if file_path not in files_data:
                        # Calcular hash e coletar metadados
                        hash_value = compute_file_hash(file_path)
                        mtime = file_path.stat().st_mtime if file_path.exists() else 0
                        
                        files_data[file_path] = {
                            'chunks': 0,
                            'hash': hash_value if hash_value else '',
                            'mtime': mtime
                        }
                    files_data[file_path]['chunks'] += 1
    
    # Se não conseguiu contar chunks via index, usar hashes apenas
    if not files_data:
        logger.warning("   ⚠️  Não foi possível contar chunks via index")
        for file_path in processed_files:
            hash_value = compute_file_hash(file_path)
            mtime = file_path.stat().st_mtime if file_path.exists() else 0
            files_data[file_path] = {
                'chunks': 0,  # Desconhecido
                'hash': hash_value if hash_value else '',
                'mtime': mtime
            }
    
    # Remover deletados do histórico
    if deleted_files:
        for file_path in deleted_files:
            history.data['files'].pop(str(file_path.absolute()), None)
        logger.info(f"   ✓ {len(deleted_files)} arquivo(s) deletado(s) removidos do histórico")
    
    # Adicionar/atualizar processados
    if files_data:
        history.add_files(files_data)
        logger.info(f"   ✓ {len(files_data)} arquivo(s) atualizados no histórico")
    
    history.save()
    logger.info("   ✓ Histórico salvo!")




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
    validate_document_paths()
    
    # 2. Carregar todos os documentos
    all_documents = load_all_documents()
    
    if all_documents is None or len(all_documents) == 0:
        logger.error("\n❌ Nenhum documento encontrado para processar!")
        return None
    
    # 2. Processar documentos com chunking inteligente
    logger.info("\n" + "=" * 70)
    logger.info("📋 Etapa 2/4: Processando documentos com chunking inteligente")
    logger.info("=" * 70)
    
    # Separar Markdown de outros formatos
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
        logger.info("\n   🧩 Processando Markdown com SentenceSplitter...")
        logger.info(f"      (Chunk size: {CHUNK_SIZE}, overlap: {CHUNK_OVERLAP})")
        from llama_index.core.node_parser import SentenceSplitter
        md_parser = SentenceSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        md_nodes = md_parser.get_nodes_from_documents(markdown_docs)
        all_nodes.extend(md_nodes)
        logger.info(f"      ✓ {len(md_nodes)} blocos criados")
    
    # Processar outros documentos
    if other_docs:
        logger.info(f"\n   📦 Processando {len(other_docs)} documentos não-Markdown...")
        from llama_index.core.node_parser import SimpleNodeParser
        simple_parser = SimpleNodeParser(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
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
    """
    Função principal com suporte a ingestão incremental (Fase 2).
    
    Detecta automaticamente mudanças (novos, modificados, deletados) e processa
    apenas o necessário, economizando tempo e recursos.
    """
    try:
        # Carregar histórico de ingestão
        history = IngestionHistory(HISTORY_FILE)
        history.load()
        stats = history.get_stats()
        
        # Escanear arquivos atuais
        current_files = scan_all_files()
        indexed_files = history.get_indexed_files()
        
        # Detectar mudanças
        new_files = detect_new_files(current_files, indexed_files)
        modified_files = detect_modified_files(current_files, indexed_files, history)
        deleted_files = detect_deleted_files(current_files, indexed_files)
        
        # Determinar modo de ingestão
        if INTERACTIVE_MODE:
            # Mostrar resumo e perguntar ao usuário
            show_changes_summary(new_files, modified_files, deleted_files,
                               indexed_files, current_files)
            mode = prompt_ingestion_mode(
                new_files | modified_files,
                stats['has_history']
            )
        else:
            # Modo automático
            if new_files or modified_files:
                mode = "incremental"
                logger.info(f"\n📝 Modo automático: {len(new_files)} novos, {len(modified_files)} modificados")
            elif deleted_files:
                mode = "skip"
                logger.info(f"\n🗑️  Apenas {len(deleted_files)} arquivo(s) deletado(s)")
            else:
                logger.info("\n📊 Nenhuma mudança detectada. Pulando ingestão.")
                exit(0)
        
        # Processar baseado no modo
        if mode == "cancel":
            logger.info("\n⚠️  Ingestão cancelada pelo usuário.")
            exit(0)
        
        elif mode == "skip":
            # Apenas limpar deletados
            if deleted_files:
                logger.info(f"\n🗑️  Limpando {len(deleted_files)} arquivo(s) deletado(s)...")
                chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
                chroma_collection = chroma_client.get_collection(CHROMA_COLLECTION_NAME)
                remove_obsolete_chunks(deleted_files, chroma_collection)
                
                for file_path in deleted_files:
                    history.data['files'].pop(str(file_path.absolute()), None)
                history.save()
                logger.info("✅ Limpeza concluída!")
            exit(0)
        
        elif mode == "full":
            # Modo full: limpar histórico e processar tudo
            logger.info("\n🔄 MODO FULL: Processando todos os arquivos...")
            history.clear()
            index = ingest_data()
        
        else:  # mode == "incremental"
            # Modo incremental: processar apenas mudanças
            files_to_process = new_files | modified_files
            
            logger.info(f"\n⚡ MODO INCREMENTAL: Processando mudanças...")
            logger.info(f"   ✨ Novos: {len(new_files)}")
            logger.info(f"   ✏️  Modificados: {len(modified_files)}")
            
            # Remover chunks obsoletos ANTES de processar
            if modified_files or deleted_files:
                logger.info(f"\n🗑️  Removendo chunks obsoletos...")
                chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
                chroma_collection = chroma_client.get_collection(CHROMA_COLLECTION_NAME)
                remove_obsolete_chunks(modified_files | deleted_files, chroma_collection)
            
            # Carregar apenas arquivos modificados
            documents = load_specific_files(files_to_process)
            
            if not documents:
                logger.error("\n❌ Nenhum documento carregado!")
                exit(1)
            
            # Processar documentos (reutilizar lógica de ingest_data)
            # TODO: Refatorar ingest_data() para aceitar documentos como parâmetro
            # Por enquanto, usar ingest_data() completo
            logger.warning("\n⚠️  Usando ingest_data() completo (refatoração pendente)")
            index = ingest_data()
            
            # Atualizar histórico com hashes
            if index:
                update_history_with_hashes(index, files_to_process, deleted_files, history)
        
        # Verificar resultado
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