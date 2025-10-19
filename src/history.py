"""
Módulo de gerenciamento de histórico de ingestão.

Rastreia arquivos já indexados para permitir ingestão incremental.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)


class IngestionHistory:
    """Gerencia histórico de arquivos indexados."""
    
    VERSION = "1.0"
    
    def __init__(self, history_file: Path):
        """
        Inicializa gerenciador de histórico.
        
        Args:
            history_file: Caminho para arquivo JSON de histórico
        """
        self.history_file = history_file
        self.data: Dict = {}
    
    def load(self) -> bool:
        """
        Carrega histórico do arquivo.
        
        Returns:
            True se carregou com sucesso, False se arquivo não existe
        """
        if not self.history_file.exists():
            logger.info("📝 Histórico não encontrado, será criado na primeira ingestão")
            self._initialize_empty()
            return False
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Validação básica
            if not self._validate():
                logger.warning("⚠️  Histórico inválido, criando novo")
                self._initialize_empty()
                return False
            
            logger.info(f"✓ Histórico carregado: {self.data['total_documents']} documentos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar histórico: {e}")
            self._initialize_empty()
            return False
    
    def save(self) -> bool:
        """
        Salva histórico no arquivo.
        
        Returns:
            True se salvou com sucesso
        """
        try:
            # Criar diretório se não existir
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup do histórico anterior
            if self.history_file.exists():
                backup_file = self.history_file.with_suffix('.json.backup')
                self.history_file.rename(backup_file)
            
            # Salvar novo histórico
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✓ Histórico salvo: {self.history_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar histórico: {e}")
            return False
    
    def get_indexed_files(self) -> Set[Path]:
        """
        Retorna conjunto de arquivos já indexados.
        
        Returns:
            Set de Paths absolutos
        """
        if not self.data or 'files' not in self.data:
            return set()
        
        return {Path(file_path) for file_path in self.data['files'].keys()}
    
    def add_files(self, files_data: Dict[Path, int]) -> None:
        """
        Adiciona arquivos ao histórico.
        
        Args:
            files_data: Dict {file_path: num_chunks}
        """
        now = datetime.now().isoformat()
        
        for file_path, num_chunks in files_data.items():
            self.data['files'][str(file_path.absolute())] = {
                'indexed_at': now,
                'chunks': num_chunks
            }
        
        # Atualizar totais
        self.data['total_documents'] = len(self.data['files'])
        self.data['total_chunks'] = sum(
            f['chunks'] for f in self.data['files'].values()
        )
        self.data['last_ingestion'] = now
    
    def clear(self) -> None:
        """Limpa histórico (força reingestão completa)."""
        self._initialize_empty()
        logger.info("🗑️  Histórico limpo")
    
    def _initialize_empty(self) -> None:
        """Inicializa estrutura vazia."""
        self.data = {
            'version': self.VERSION,
            'last_ingestion': None,
            'total_documents': 0,
            'total_chunks': 0,
            'files': {}
        }
    
    def _validate(self) -> bool:
        """
        Valida estrutura do histórico.
        
        Returns:
            True se válido
        """
        required_keys = {'version', 'files'}
        if not all(key in self.data for key in required_keys):
            return False
        
        if self.data['version'] != self.VERSION:
            logger.warning(f"⚠️  Versão do histórico incompatível: {self.data['version']}")
            return False
        
        return True
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do histórico.
        
        Returns:
            Dict com estatísticas
        """
        return {
            'total_documents': self.data.get('total_documents', 0),
            'total_chunks': self.data.get('total_chunks', 0),
            'last_ingestion': self.data.get('last_ingestion'),
            'has_history': len(self.data.get('files', {})) > 0
        }
