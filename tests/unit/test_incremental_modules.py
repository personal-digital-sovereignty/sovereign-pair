import sys
from pathlib import Path
import pytest

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from history import IngestionHistory
from diff import detect_new_files, get_unchanged_files

@pytest.fixture
def temp_history_file(tmp_path):
    """Fixture que provê um caminho de arquivo temporário limpo."""
    history_file = tmp_path / "test_history.json"
    yield history_file
    if history_file.exists():
        history_file.unlink()

def test_history(temp_history_file):
    """Testa o módulo de IngestionHistory."""
    history = IngestionHistory(temp_history_file)
    
    # 1. Carregar histórico inexistente
    assert history.load() is False, "Deve retornar False para histórico inexistente"
    
    # 2. Adicionar arquivos
    files_data = {
        Path("/tmp/doc1.md"): {'chunks': 3, 'hash': 'abc', 'mtime': 123},
        Path("/tmp/doc2.md"): {'chunks': 5, 'hash': 'def', 'mtime': 456},
    }
    history.add_files(files_data)
    
    # 3. Salvar histórico
    assert history.save() is True, "Deve retornar True ao salvar"
    assert temp_history_file.exists(), "Arquivo deve existir"
    
    # 4. Carregar histórico existente
    history2 = IngestionHistory(temp_history_file)
    assert history2.load() is True, "Deve retornar True para histórico existente"
    
    # 5. Verificar dados
    indexed = history2.get_indexed_files()
    assert len(indexed) == 2, f"Deve ter 2 arquivos, tem {len(indexed)}"
    
    # 6. Estatísticas
    stats = history2.get_stats()
    assert stats['total_documents'] == 2
    assert stats['total_chunks'] == 8
    assert stats['has_history'] is True

def test_diff_detect_new_files():
    """Testa detecção de novos arquivos no diff."""
    current = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md"), Path("/tmp/doc3.md")}
    indexed = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md")}
    
    new_files = detect_new_files(current, indexed)
    assert len(new_files) == 1
    assert Path("/tmp/doc3.md") in new_files

def test_diff_no_new_files():
    current = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md")}
    indexed = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md")}
    
    new_files = detect_new_files(current, indexed)
    assert len(new_files) == 0

def test_diff_unchanged_files():
    current = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md"), Path("/tmp/doc3.md")}
    indexed = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md")}
    
    unchanged = get_unchanged_files(current, indexed)
    assert len(unchanged) == 2

def test_interactive_imports():
    """Testa apenas as importações do módulo interativo."""
    from interactive import show_changes_summary, prompt_ingestion_mode, confirm_action
    assert show_changes_summary is not None
    assert prompt_ingestion_mode is not None
    assert confirm_action is not None
