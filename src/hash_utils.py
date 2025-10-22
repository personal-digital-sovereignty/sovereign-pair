"""
Utilitários para hashing de arquivos.

Fornece funções para calcular hashes SHA256 de arquivos,
usado para detectar modificações de conteúdo na ingestão incremental.
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> Optional[str]:
    """
    Calcula hash do conteúdo do arquivo.
    
    Lê o arquivo em chunks para eficiência com arquivos grandes.
    
    Args:
        file_path: Caminho do arquivo
        algorithm: Algoritmo de hash (padrão: sha256)
        
    Returns:
        Hash em formato "algorithm:hexdigest", ou None se erro
        
    Examples:
        >>> compute_file_hash(Path("doc.md"))
        'sha256:a3b2c1d4e5f6...'
    """
    if not file_path.exists():
        logger.warning(f"⚠️  Arquivo não existe: {file_path}")
        return None
    
    if not file_path.is_file():
        logger.warning(f"⚠️  Não é um arquivo: {file_path}")
        return None
    
    try:
        # Criar hasher
        if algorithm == "sha256":
            hasher = hashlib.sha256()
        elif algorithm == "md5":
            hasher = hashlib.md5()
        else:
            logger.error(f"❌ Algoritmo não suportado: {algorithm}")
            return None
        
        # Ler arquivo em chunks (8KB por vez)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        
        # Retornar hash com prefixo do algoritmo
        return f"{algorithm}:{hasher.hexdigest()}"
        
    except PermissionError:
        logger.error(f"❌ Sem permissão para ler: {file_path}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro ao calcular hash de {file_path.name}: {e}")
        return None


def compute_files_hashes(file_paths: set[Path]) -> dict[Path, Optional[str]]:
    """
    Calcula hashes de múltiplos arquivos.
    
    Args:
        file_paths: Conjunto de caminhos de arquivos
        
    Returns:
        Dicionário {file_path: hash}
    """
    hashes = {}
    
    for file_path in file_paths:
        hashes[file_path] = compute_file_hash(file_path)
    
    return hashes


def verify_file_hash(file_path: Path, expected_hash: str) -> bool:
    """
    Verifica se o hash de um arquivo corresponde ao esperado.
    
    Args:
        file_path: Caminho do arquivo
        expected_hash: Hash esperado (formato "algorithm:hexdigest")
        
    Returns:
        True se o hash corresponde, False caso contrário
    """
    current_hash = compute_file_hash(file_path)
    
    if current_hash is None:
        return False
    
    return current_hash == expected_hash
