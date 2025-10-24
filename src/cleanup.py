"""
Módulo de limpeza de chunks obsoletos do ChromaDB.

Remove chunks de arquivos modificados ou deletados durante ingestão incremental.
"""

import logging
from pathlib import Path
from typing import Set, Optional

logger = logging.getLogger(__name__)


def remove_obsolete_chunks(
    file_paths: Set[Path],
    chroma_collection,
    dry_run: bool = False
) -> int:
    """
    Remove chunks de arquivos obsoletos do ChromaDB.
    
    Args:
        file_paths: Conjunto de paths de arquivos a remover
        chroma_collection: Coleção ChromaDB
        dry_run: Se True, apenas simula remoção sem executar
        
    Returns:
        Número de chunks removidos
    """
    if not file_paths:
        logger.info("✓ Nenhum chunk para remover")
        return 0
    
    total_removed = 0
    
    logger.info(f"\n🗑️  Removendo chunks de {len(file_paths)} arquivo(s)...")
    
    for file_path in file_paths:
        try:
            # Buscar chunks deste arquivo
            # ChromaDB usa metadata para filtrar
            results = chroma_collection.get(
                where={"file_path": str(file_path.absolute())}
            )
            
            if results and results.get('ids'):
                chunk_ids = results['ids']
                num_chunks = len(chunk_ids)
                
                if dry_run:
                    logger.info(f"   [DRY-RUN] Removeria {num_chunks} chunks de {file_path.name}")
                else:
                    # Deletar chunks
                    chroma_collection.delete(ids=chunk_ids)
                    total_removed += num_chunks
                    logger.info(f"   ✓ Removidos {num_chunks} chunks de {file_path.name}")
            else:
                logger.debug(f"   ⚠️  Nenhum chunk encontrado para {file_path.name}")
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao remover chunks de {file_path.name}: {e}")
    
    if not dry_run:
        logger.info(f"✓ Total: {total_removed} chunks removidos")
    
    return total_removed


def count_chunks_for_files(
    file_paths: Set[Path],
    chroma_collection
) -> dict[Path, int]:
    """
    Conta quantos chunks cada arquivo tem no ChromaDB.
    
    Args:
        file_paths: Conjunto de paths de arquivos
        chroma_collection: Coleção ChromaDB
        
    Returns:
        Dicionário {file_path: num_chunks}
    """
    chunk_counts = {}
    
    for file_path in file_paths:
        try:
            results = chroma_collection.get(
                where={"file_path": str(file_path.absolute())}
            )
            
            if results and results.get('ids'):
                chunk_counts[file_path] = len(results['ids'])
            else:
                chunk_counts[file_path] = 0
                
        except Exception as e:
            logger.error(f"❌ Erro ao contar chunks de {file_path.name}: {e}")
            chunk_counts[file_path] = 0
    
    return chunk_counts


def verify_cleanup(
    file_paths: Set[Path],
    chroma_collection
) -> bool:
    """
    Verifica se os chunks foram realmente removidos.
    
    Args:
        file_paths: Conjunto de paths de arquivos que deveriam estar limpos
        chroma_collection: Coleção ChromaDB
        
    Returns:
        True se todos os chunks foram removidos, False caso contrário
    """
    for file_path in file_paths:
        try:
            results = chroma_collection.get(
                where={"file_path": str(file_path.absolute())}
            )
            
            if results and results.get('ids'):
                logger.warning(f"⚠️  Ainda existem {len(results['ids'])} chunks de {file_path.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar {file_path.name}: {e}")
            return False
    
    logger.info("✓ Verificação OK: todos os chunks foram removidos")
    return True
