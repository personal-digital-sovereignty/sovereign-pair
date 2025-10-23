"""
Módulo de detecção de mudanças entre execuções.

Compara arquivos atuais com histórico para identificar novos, modificados e deletados.
"""

import logging
from pathlib import Path
from typing import Set

logger = logging.getLogger(__name__)


def detect_new_files(
    current_files: Set[Path],
    indexed_files: Set[Path]
) -> Set[Path]:
    """
    Detecta arquivos novos que não estão no histórico.
    
    Args:
        current_files: Conjunto de arquivos encontrados atualmente
        indexed_files: Conjunto de arquivos já indexados (do histórico)
    
    Returns:
        Conjunto de arquivos novos
    """
    new_files = current_files - indexed_files
    
    if new_files:
        logger.info(f"✨ {len(new_files)} novo(s) arquivo(s) detectado(s)")
    else:
        logger.info("✓ Nenhum arquivo novo detectado")
    
    return new_files


def detect_modified_files(
    current_files: Set[Path],
    indexed_files: Set[Path],
    history
) -> Set[Path]:
    """
    Detecta arquivos que foram modificados desde a última ingestão.
    
    Compara hashes de conteúdo para arquivos que existem em ambos os conjuntos.
    
    Args:
        current_files: Arquivos atuais no filesystem
        indexed_files: Arquivos no histórico
        history: Instância do IngestionHistory
        
    Returns:
        Conjunto de arquivos modificados
    """
    from hash_utils import compute_file_hash
    
    # Arquivos que existem em ambos
    common_files = current_files & indexed_files
    modified = set()
    
    for file_path in common_files:
        # Calcular hash atual
        current_hash = compute_file_hash(file_path)
        if not current_hash:
            continue
            
        # Obter hash do histórico
        file_data = history.data['files'].get(str(file_path.absolute()), {})
        stored_hash = file_data.get('content_hash', '')
        
        # Se não há hash armazenado, considerar modificado (migração v1.0)
        if not stored_hash:
            modified.add(file_path)
            logger.debug(f"   📝 Sem hash no histórico: {file_path.name}")
            continue
        
        # Comparar hashes
        if current_hash != stored_hash:
            modified.add(file_path)
            logger.debug(f"   ✏️  Modificado: {file_path.name}")
    
    if modified:
        logger.info(f"✏️  {len(modified)} arquivo(s) modificado(s)")
    else:
        logger.info("✓ Nenhum arquivo modificado")
    
    return modified


def detect_deleted_files(
    current_files: Set[Path],
    indexed_files: Set[Path]
) -> Set[Path]:
    """
    Detecta arquivos que foram deletados desde a última ingestão.
    
    Args:
        current_files: Arquivos atuais
        indexed_files: Arquivos no histórico
        
    Returns:
        Conjunto de arquivos deletados
    """
    deleted = indexed_files - current_files
    
    if deleted:
        logger.info(f"🗑️  {len(deleted)} arquivo(s) deletado(s)")
        for file_path in list(deleted)[:5]:  # Mostrar até 5
            logger.debug(f"   🗑️  {file_path.name}")
        if len(deleted) > 5:
            logger.debug(f"   ... e mais {len(deleted) - 5} arquivo(s)")
    else:
        logger.info("✓ Nenhum arquivo deletado")
    
    return deleted


def get_unchanged_files(
    current_files: Set[Path],
    indexed_files: Set[Path]
) -> Set[Path]:
    """
    Retorna arquivos que já estão indexados.
    
    Args:
        current_files: Conjunto de arquivos encontrados atualmente
        indexed_files: Conjunto de arquivos já indexados
    
    Returns:
        Conjunto de arquivos sem mudança
    """
    unchanged = current_files & indexed_files
    return unchanged
