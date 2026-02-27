#!/usr/bin/env python3
"""
Script de validação do estado do sistema de ingestão incremental.

Valida ChromaDB, histórico e consistência entre eles.
"""

import json
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import chromadb
    from config import CHROMA_DIR, CHROMA_COLLECTION_NAME, HISTORY_FILE
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Certifique-se de que as dependências estão instaladas")
    sys.exit(1)


def validate_history():
    """Valida arquivo de histórico"""
    print("\n" + "=" * 70)
    print("📋 VALIDANDO HISTÓRICO")
    print("=" * 70)
    
    if not HISTORY_FILE.exists():
        print(f"❌ Histórico não encontrado: {HISTORY_FILE}")
        return False
    
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        
        # Validar versão
        version = history.get('version', '1.0')
        print(f"   Versão: {version}")
        
        if version != '1.1':
            print(f"   ⚠️  Versão esperada: 1.1, encontrada: {version}")
        
        # Validar arquivos
        files = history.get('files', {})
        print(f"   Arquivos no histórico: {len(files)}")
        
        # Validar campos obrigatórios
        errors = 0
        for file_path, file_data in files.items():
            # Verificar campos v1.1
            if 'content_hash' not in file_data:
                print(f"   ❌ {file_path}: falta content_hash")
                errors += 1
            elif len(file_data['content_hash']) != 64:
                print(f"   ❌ {file_path}: hash inválido (não é SHA256)")
                errors += 1
            
            if 'modified_at' not in file_data:
                print(f"   ❌ {file_path}: falta modified_at")
                errors += 1
            
            if 'chunks' not in file_data:
                print(f"   ❌ {file_path}: falta chunks")
                errors += 1
        
        if errors == 0:
            print(f"   ✅ Todos os {len(files)} arquivos válidos")
            return True
        else:
            print(f"   ❌ {errors} erro(s) encontrado(s)")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def validate_chromadb():
    """Valida ChromaDB"""
    print("\n" + "=" * 70)
    print("💾 VALIDANDO CHROMADB")
    print("=" * 70)
    
    if not CHROMA_DIR.exists():
        print(f"❌ ChromaDB não encontrado: {CHROMA_DIR}")
        return False, {}
    
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(CHROMA_COLLECTION_NAME)
        
        # Contar chunks
        total_chunks = collection.count()
        print(f"   Total de chunks: {total_chunks}")
        
        # Agrupar por arquivo
        all_data = collection.get(include=['metadatas'])
        chunks_by_file = {}
        
        for metadata in all_data['metadatas']:
            file_path = metadata.get('file_path', 'unknown')
            chunks_by_file[file_path] = chunks_by_file.get(file_path, 0) + 1
        
        print(f"   Arquivos únicos: {len(chunks_by_file)}")
        
        # Mostrar top 5
        if chunks_by_file:
            print("\n   Top 5 arquivos por chunks:")
            sorted_files = sorted(chunks_by_file.items(), key=lambda x: x[1], reverse=True)
            for file_path, count in sorted_files[:5]:
                print(f"      {count:3d} chunks: {file_path}")
        
        print("\n   ✅ ChromaDB válido")
        return True, chunks_by_file
        
    except Exception as e:
        print(f"❌ Erro ao acessar ChromaDB: {e}")
        return False, {}


def validate_consistency(chunks_by_file):
    """Valida consistência entre histórico e ChromaDB"""
    print("\n" + "=" * 70)
    print("🔍 VALIDANDO CONSISTÊNCIA")
    print("=" * 70)
    
    if not HISTORY_FILE.exists():
        print("❌ Histórico não encontrado")
        return False
    
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        
        files_in_history = set(history.get('files', {}).keys())
        files_in_chromadb = set(chunks_by_file.keys())
        
        print(f"   Arquivos no histórico: {len(files_in_history)}")
        print(f"   Arquivos no ChromaDB: {len(files_in_chromadb)}")
        
        # Arquivos apenas no histórico
        only_history = files_in_history - files_in_chromadb
        if only_history:
            print(f"\n   ⚠️  {len(only_history)} arquivo(s) apenas no histórico:")
            for file_path in list(only_history)[:5]:
                print(f"      - {file_path}")
            if len(only_history) > 5:
                print(f"      ... e mais {len(only_history) - 5}")
        
        # Arquivos apenas no ChromaDB
        only_chromadb = files_in_chromadb - files_in_history
        if only_chromadb:
            print(f"\n   ⚠️  {len(only_chromadb)} arquivo(s) apenas no ChromaDB:")
            for file_path in list(only_chromadb)[:5]:
                print(f"      - {file_path}")
            if len(only_chromadb) > 5:
                print(f"      ... e mais {len(only_chromadb) - 5}")
        
        # Verificar contagem de chunks
        mismatches = 0
        for file_path in files_in_history & files_in_chromadb:
            history_chunks = history['files'][file_path].get('chunks', 0)
            chromadb_chunks = chunks_by_file[file_path]
            
            if history_chunks != chromadb_chunks:
                if mismatches < 5:  # Mostrar apenas primeiros 5
                    print(f"\n   ⚠️  {file_path}:")
                    print(f"      Histórico: {history_chunks} chunks")
                    print(f"      ChromaDB: {chromadb_chunks} chunks")
                mismatches += 1
        
        if mismatches > 5:
            print(f"\n   ⚠️  ... e mais {mismatches - 5} arquivo(s) com divergência")
        
        # Resultado
        if not only_history and not only_chromadb and mismatches == 0:
            print("\n   ✅ Histórico e ChromaDB consistentes")
            return True
        else:
            print("\n   ⚠️  Inconsistências encontradas")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao validar consistência: {e}")
        return False


def main():
    """Executa todas as validações"""
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "VALIDAÇÃO DO SISTEMA" + " " * 33 + "║")
    print("╚" + "=" * 68 + "╝")
    
    results = {
        'history': validate_history(),
        'chromadb': validate_chromadb(),
    }
    
    chunks_by_file = results['chromadb'][1] if isinstance(results['chromadb'], tuple) else {}
    results['chromadb'] = results['chromadb'][0] if isinstance(results['chromadb'], tuple) else results['chromadb']
    results['consistency'] = validate_consistency(chunks_by_file)
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {check.capitalize():15s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TODAS AS VALIDAÇÕES PASSARAM")
    else:
        print("❌ ALGUMAS VALIDAÇÕES FALHARAM")
    print("=" * 70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
