"""
Módulo de detecção de mudanças entre execuções.

Compara arquivos atuais com histórico para identificar novos arquivos.
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
