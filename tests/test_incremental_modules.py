#!/usr/bin/env python3
"""
Script de teste para validar os módulos de ingestão incremental.

Testa: history.py, diff.py, interactive.py
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from history import IngestionHistory
from diff import detect_new_files, get_unchanged_files

def test_history():
    """Testa módulo de histórico."""
    print("=" * 70)
    print("🧪 TESTANDO: history.py")
    print("=" * 70)
    
    # Criar histórico temporário
    test_file = Path("/tmp/test_history.json")
    if test_file.exists():
        test_file.unlink()
    
    history = IngestionHistory(test_file)
    
    # Teste 1: Carregar histórico inexistente
    print("\n1. Carregando histórico inexistente...")
    result = history.load()
    assert result == False, "Deve retornar False para histórico inexistente"
    print("   ✓ Retornou False corretamente")
    
    # Teste 2: Adicionar arquivos
    print("\n2. Adicionando arquivos ao histórico...")
    files_data = {
        Path("/tmp/doc1.md"): 3,
        Path("/tmp/doc2.md"): 5,
    }
    history.add_files(files_data)
    print(f"   ✓ Adicionados {len(files_data)} arquivos")
    
    # Teste 3: Salvar histórico
    print("\n3. Salvando histórico...")
    result = history.save()
    assert result == True, "Deve retornar True ao salvar"
    assert test_file.exists(), "Arquivo deve existir"
    print("   ✓ Histórico salvo com sucesso")
    
    # Teste 4: Carregar histórico existente
    print("\n4. Carregando histórico existente...")
    history2 = IngestionHistory(test_file)
    result = history2.load()
    assert result == True, "Deve retornar True para histórico existente"
    print("   ✓ Histórico carregado com sucesso")
    
    # Teste 5: Verificar dados
    print("\n5. Verificando dados carregados...")
    indexed = history2.get_indexed_files()
    assert len(indexed) == 2, f"Deve ter 2 arquivos, tem {len(indexed)}"
    print(f"   ✓ {len(indexed)} arquivos indexados")
    
    # Teste 6: Estatísticas
    print("\n6. Verificando estatísticas...")
    stats = history2.get_stats()
    assert stats['total_documents'] == 2
    assert stats['total_chunks'] == 8
    assert stats['has_history'] == True
    print(f"   ✓ Documentos: {stats['total_documents']}")
    print(f"   ✓ Chunks: {stats['total_chunks']}")
    
    # Limpar
    test_file.unlink()
    print("\n✅ Todos os testes de history.py passaram!")
    return True


def test_diff():
    """Testa módulo de diff."""
    print("\n" + "=" * 70)
    print("🧪 TESTANDO: diff.py")
    print("=" * 70)
    
    # Teste 1: Detectar novos arquivos
    print("\n1. Detectando novos arquivos...")
    current = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md"), Path("/tmp/doc3.md")}
    indexed = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md")}
    
    new_files = detect_new_files(current, indexed)
    assert len(new_files) == 1, f"Deve ter 1 novo, tem {len(new_files)}"
    assert Path("/tmp/doc3.md") in new_files
    print(f"   ✓ {len(new_files)} novo arquivo detectado")
    
    # Teste 2: Sem novos arquivos
    print("\n2. Testando sem novos arquivos...")
    current2 = {Path("/tmp/doc1.md"), Path("/tmp/doc2.md")}
    new_files2 = detect_new_files(current2, indexed)
    assert len(new_files2) == 0, f"Não deve ter novos, tem {len(new_files2)}"
    print("   ✓ Nenhum novo arquivo (correto)")
    
    # Teste 3: Arquivos sem mudança
    print("\n3. Detectando arquivos sem mudança...")
    unchanged = get_unchanged_files(current, indexed)
    assert len(unchanged) == 2, f"Deve ter 2 sem mudança, tem {len(unchanged)}"
    print(f"   ✓ {len(unchanged)} arquivos sem mudança")
    
    print("\n✅ Todos os testes de diff.py passaram!")
    return True


def test_interactive():
    """Testa módulo interactive (apenas imports)."""
    print("\n" + "=" * 70)
    print("🧪 TESTANDO: interactive.py")
    print("=" * 70)
    
    print("\n1. Verificando imports...")
    from interactive import show_changes_summary, prompt_ingestion_mode, confirm_action
    print("   ✓ Todos os imports funcionam")
    
    print("\n✅ Módulo interactive.py OK!")
    print("   (Testes interativos devem ser feitos manualmente)")
    return True


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 70)
    print("🚀 INICIANDO TESTES DOS MÓDULOS DE INGESTÃO INCREMENTAL")
    print("=" * 70)
    
    try:
        # Executar testes
        test_history()
        test_diff()
        test_interactive()
        
        # Resumo final
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 70)
        print("\n📊 Resumo:")
        print("   ✓ history.py: 6 testes passaram")
        print("   ✓ diff.py: 3 testes passaram")
        print("   ✓ interactive.py: Imports OK")
        print("\n🎉 Módulos prontos para integração!")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
