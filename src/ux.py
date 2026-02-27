"""
Módulo de UX - Melhorias de experiência do usuário.

Fornece barras de progresso, logs coloridos, estimativas de tempo
e resumos estatísticos detalhados.

Versão 1.0
"""

import time
import logging

logger = logging.getLogger(__name__)

# Tentar importar colorama para logs coloridos
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    logger.warning("colorama não disponível, logs sem cores")


class ColoredLogger:
    """Logger com cores para melhor legibilidade."""
    
    @staticmethod
    def success(msg: str):
        """Log de sucesso (verde)"""
        if COLORAMA_AVAILABLE:
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} {msg}")
        else:
            print(f"✓ {msg}")
    
    @staticmethod
    def info(msg: str):
        """Log informativo (azul)"""
        if COLORAMA_AVAILABLE:
            print(f"{Fore.BLUE}ℹ{Style.RESET_ALL} {msg}")
        else:
            print(f"ℹ {msg}")
    
    @staticmethod
    def warning(msg: str):
        """Log de aviso (amarelo)"""
        if COLORAMA_AVAILABLE:
            print(f"{Fore.YELLOW}⚠{Style.RESET_ALL} {msg}")
        else:
            print(f"⚠ {msg}")
    
    @staticmethod
    def error(msg: str):
        """Log de erro (vermelho)"""
        if COLORAMA_AVAILABLE:
            print(f"{Fore.RED}✗{Style.RESET_ALL} {msg}")
        else:
            print(f"✗ {msg}")
    
    @staticmethod
    def header(msg: str):
        """Cabeçalho destacado (ciano)"""
        if COLORAMA_AVAILABLE:
            print(f"\n{Fore.CYAN}{'='*70}")
            print(f"{msg}")
            print(f"{'='*70}{Style.RESET_ALL}\n")
        else:
            print(f"\n{'='*70}")
            print(f"{msg}")
            print(f"{'='*70}\n")


def estimate_processing_time(num_files: int, avg_time_per_file: float = 0.5) -> str:
    """
    Estima tempo de processamento.
    
    Args:
        num_files: Número de arquivos
        avg_time_per_file: Tempo médio por arquivo (segundos)
    
    Returns:
        String formatada (ex: "~2m 30s")
    
    Examples:
        >>> estimate_processing_time(10)
        '~5s'
        >>> estimate_processing_time(200)
        '~1m 40s'
    """
    total_seconds = num_files * avg_time_per_file
    
    if total_seconds < 60:
        return f"~{int(total_seconds)}s"
    elif total_seconds < 3600:
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        return f"~{minutes}m {seconds}s"
    else:
        hours = int(total_seconds / 3600)
        minutes = int((total_seconds % 3600) / 60)
        return f"~{hours}h {minutes}m"


def format_bytes(bytes_value: int) -> str:
    """
    Formata bytes em formato legível.
    
    Args:
        bytes_value: Valor em bytes
    
    Returns:
        String formatada (ex: "1.5 MB")
    
    Examples:
        >>> format_bytes(1024)
        '1.0 KB'
        >>> format_bytes(1536000)
        '1.5 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Formata duração em formato legível.
    
    Args:
        seconds: Duração em segundos
    
    Returns:
        String formatada (ex: "2m 30s")
    
    Examples:
        >>> format_duration(5.5)
        '5.5s'
        >>> format_duration(125)
        '2m 5s'
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


class ProcessingStats:
    """Coleta e exibe estatísticas de processamento."""
    
    def __init__(self):
        self.start_time = time.time()
        self.files_processed = 0
        self.chunks_created = 0
        self.total_bytes = 0
        self.new_files = 0
        self.modified_files = 0
        self.deleted_files = 0
        self.unchanged_files = 0
        self.errors = 0
        self.is_incremental = False
    
    def mark_start(self):
        """Marca início do processamento"""
        self.start_time = time.time()
    
    def get_duration(self) -> float:
        """Retorna duração em segundos"""
        return time.time() - self.start_time
    
    def get_files_per_second(self) -> float:
        """Retorna taxa de processamento"""
        duration = self.get_duration()
        if duration > 0:
            return self.files_processed / duration
        return 0.0
    
    def show_summary(self):
        """Mostra resumo estatístico detalhado"""
        duration = self.get_duration()
        files_per_sec = self.get_files_per_second()
        
        print("\n" + "="*70)
        print("📊 ESTATÍSTICAS DE PROCESSAMENTO")
        print("="*70)
        
        print(f"\n⏱️  Tempo total: {format_duration(duration)}")
        print(f"📁 Arquivos processados: {self.files_processed}")
        
        if self.chunks_created > 0:
            print(f"📦 Chunks criados: {self.chunks_created}")
        
        if self.total_bytes > 0:
            print(f"💾 Tamanho total: {format_bytes(self.total_bytes)}")
        
        if files_per_sec > 0:
            print(f"⚡ Velocidade: {files_per_sec:.2f} arquivos/s")
        
        if self.is_incremental:
            print("\n🚀 Modo incremental:")
            print(f"   ✨ Novos: {self.new_files}")
            print(f"   ✏️  Modificados: {self.modified_files}")
            print(f"   🗑️  Deletados: {self.deleted_files}")
            print(f"   ⏭️  Ignorados: {self.unchanged_files}")
        
        if self.errors > 0:
            print(f"\n⚠️  Erros: {self.errors}")
        
        print("="*70 + "\n")
    
    def to_dict(self) -> dict:
        """Retorna estatísticas como dicionário"""
        return {
            'duration': self.get_duration(),
            'files_processed': self.files_processed,
            'chunks_created': self.chunks_created,
            'total_bytes': self.total_bytes,
            'files_per_second': self.get_files_per_second(),
            'incremental': self.is_incremental,
            'new_files': self.new_files,
            'modified_files': self.modified_files,
            'deleted_files': self.deleted_files,
            'unchanged_files': self.unchanged_files,
            'errors': self.errors
        }


def show_welcome_banner():
    """Mostra banner de boas-vindas"""
    if COLORAMA_AVAILABLE:
        print(f"\n{Fore.CYAN}╔{'═'*68}╗")
        print(f"║{' '*15}INGESTÃO INCREMENTAL{' '*33}║")
        print(f"╚{'═'*68}╝{Style.RESET_ALL}\n")
    else:
        print(f"\n╔{'═'*68}╗")
        print(f"║{' '*15}INGESTÃO INCREMENTAL{' '*33}║")
        print(f"╚{'═'*68}╝\n")


# Instância global de estatísticas
stats = ProcessingStats()
