"""
Utilitários para cálculo de hashes SHA256 de arquivos.

Versão 2.0: Otimizações de performance
- Paralelização com ThreadPoolExecutor
- Cache LRU em memória
- Barra de progresso
"""

import hashlib
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

# Configuração
HASH_CHUNK_SIZE = 8192  # 8KB por chunk
MAX_CACHE_SIZE = 1000   # Máximo de hashes em cache


def compute_file_hash(file_path: Path) -> str:
    """
    Calcula hash SHA256 de um arquivo.
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        Hash SHA256 (64 caracteres hexadecimais)
    
    Raises:
        FileNotFoundError: Se arquivo não existe
        PermissionError: Se sem permissão de leitura
    """
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            # Ler em chunks para eficiência de memória
            for byte_block in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {file_path}")
        raise
    except PermissionError:
        logger.error(f"Sem permissão para ler: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Erro ao calcular hash de {file_path}: {e}")
        raise


@lru_cache(maxsize=MAX_CACHE_SIZE)
def compute_file_hash_cached(file_path_str: str, mtime: float) -> str:
    """
    Calcula hash SHA256 com cache baseado em mtime.
    
    O cache usa mtime como parte da chave, então se o arquivo
    for modificado, o hash será recalculado automaticamente.
    
    Args:
        file_path_str: Caminho do arquivo (string para ser hashable)
        mtime: Timestamp de modificação do arquivo
    
    Returns:
        Hash SHA256 (64 caracteres hexadecimais)
    """
    return compute_file_hash(Path(file_path_str))


def get_file_hash_with_cache(file_path: Path) -> str:
    """
    Obtém hash do arquivo usando cache quando possível.
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        Hash SHA256 (64 caracteres hexadecimais)
    """
    try:
        mtime = file_path.stat().st_mtime
        return compute_file_hash_cached(str(file_path), mtime)
    except Exception as e:
        logger.warning(f"Erro ao usar cache para {file_path}, calculando direto: {e}")
        return compute_file_hash(file_path)


def compute_hashes_parallel(
    files: list[Path],
    max_workers: int = 4,
    use_cache: bool = True,
    show_progress: bool = True
) -> dict[str, str]:
    """
    Calcula hashes SHA256 em paralelo para múltiplos arquivos.
    
    Args:
        files: Lista de arquivos
        max_workers: Número de threads (default: 4)
        use_cache: Se True, usa cache LRU (default: True)
        show_progress: Se True, mostra barra de progresso (default: True)
    
    Returns:
        Dict {file_path: hash}
    
    Example:
        >>> files = [Path("file1.txt"), Path("file2.txt")]
        >>> hashes = compute_hashes_parallel(files, max_workers=4)
        >>> print(hashes)
        {'file1.txt': 'abc123...', 'file2.txt': 'def456...'}
    """
    hashes = {}
    errors = []
    
    # Escolher função de hash
    hash_func = get_file_hash_with_cache if use_cache else compute_file_hash
    
    # Processar em paralelo
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submeter todas as tarefas
        future_to_file = {
            executor.submit(hash_func, f): f 
            for f in files
        }
        
        # Processar resultados
        if show_progress:
            try:
                from tqdm import tqdm
                iterator = tqdm(
                    as_completed(future_to_file),
                    total=len(files),
                    desc="Calculando hashes",
                    unit="arquivo"
                )
            except ImportError:
                logger.warning("tqdm não disponível, sem barra de progresso")
                iterator = as_completed(future_to_file)
        else:
            iterator = as_completed(future_to_file)
        
        for future in iterator:
            file_path = future_to_file[future]
            try:
                hash_value = future.result()
                hashes[str(file_path)] = hash_value
            except Exception as e:
                logger.error(f"Erro ao calcular hash de {file_path}: {e}")
                errors.append((file_path, str(e)))
    
    # Log de erros
    if errors:
        logger.warning(f"{len(errors)} arquivo(s) com erro ao calcular hash")
        for file_path, error in errors[:5]:  # Mostrar apenas primeiros 5
            logger.warning(f"  - {file_path}: {error}")
        if len(errors) > 5:
            logger.warning(f"  ... e mais {len(errors) - 5} erro(s)")
    
    return hashes


def clear_hash_cache():
    """Limpa o cache de hashes."""
    compute_file_hash_cached.cache_clear()
    logger.info("Cache de hashes limpo")


def get_cache_info() -> dict:
    """
    Retorna informações sobre o cache de hashes.
    
    Returns:
        Dict com hits, misses, maxsize e currsize
    """
    info = compute_file_hash_cached.cache_info()
    return {
        'hits': info.hits,
        'misses': info.misses,
        'maxsize': info.maxsize,
        'currsize': info.currsize,
        'hit_rate': info.hits / (info.hits + info.misses) if (info.hits + info.misses) > 0 else 0.0
    }


# Função de conveniência para compatibilidade
def compute_hashes(files: list[Path], parallel: bool = True, **kwargs) -> dict[str, str]:
    """
    Calcula hashes de arquivos (wrapper de conveniência).
    
    Args:
        files: Lista de arquivos
        parallel: Se True, usa processamento paralelo (default: True)
        **kwargs: Argumentos adicionais para compute_hashes_parallel
    
    Returns:
        Dict {file_path: hash}
    """
    if parallel and len(files) > 1:
        return compute_hashes_parallel(files, **kwargs)
    else:
        # Sequencial para poucos arquivos
        return {str(f): compute_file_hash(f) for f in files}
