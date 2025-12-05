import logging
import sys
import os
from pathlib import Path

# Adicionar ../src ao path para importar módulos do projeto
sys.path.append(str(Path(__file__).parent.parent / "src"))

import chromadb
from history import IngestionHistory
from config import HISTORY_FILE, CHROMA_DIR, CHROMA_COLLECTION_NAME

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def repair_history():
    print(f"\n🔧 Iniciando reparo do histórico: {HISTORY_FILE}")
    print("-" * 60)
    
    if not HISTORY_FILE.exists():
        print("❌ Arquivo de histórico não encontrado.")
        return

    # Carregar histórico
    history = IngestionHistory(HISTORY_FILE)
    history.load()
    
    # Conectar ao ChromaDB
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_collection(CHROMA_COLLECTION_NAME)
    except Exception as e:
        print(f"❌ Erro ao conectar ao ChromaDB: {e}")
        return

    files_data = history.data.get('files', {})
    updated_count = 0
    
    print(f"📂 Verificando {len(files_data)} arquivos no histórico...")
    
    # Iterar sobre arquivos e corrigir contagem
    for file_path, data in files_data.items():
        # Buscar chunks reais no ChromaDB usando metadata
        # (Chroma armazena file_path no metadata)
        try:
            # Query apenas para contar (limit 1 é pouco, precisamos de count)
            # A API do Chroma para count com filtro é o get()
            result = collection.get(
                where={"file_path": file_path},
                include=["metadatas"]
            )
            
            real_chunks = len(result['ids']) if result and 'ids' in result else 0
            
            stored_chunks = data.get('chunks', 0)
            
            if real_chunks != stored_chunks:
                print(f"   ✏️  Corrigindo {Path(file_path).name}: {stored_chunks} -> {real_chunks} chunks")
                history.data['files'][file_path]['chunks'] = real_chunks
                updated_count += 1
                
        except Exception as e:
            print(f"   ⚠️  Erro ao verificar {Path(file_path).name}: {e}")

    if updated_count > 0:
        print("-" * 60)
        print(f"💾 Salvando correções para {updated_count} arquivos...")
        history.save()
        print("✅ Histórico reparado com sucesso!")
    else:
        print("-" * 60)
        print("✅ Nenhuma inconsistência encontrada.")

if __name__ == "__main__":
    repair_history()
