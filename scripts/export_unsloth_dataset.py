import sqlite3
import json
import os
import argparse
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "data" / "sovereign_memory.db"
OUTPUT_PATH = ROOT_DIR / "data" / "cognitive_distillation.jsonl"

def detect_thinking_tags(content: str) -> bool:
    """Valida se o modelo realmente refletiu na resposta usando <thinking>."""
    if not content:
        return False
    return "<thinking>" in content and "</thinking>" in content

def export_to_sharegpt():
    if not DB_PATH.exists():
        print(f"❌ [Unsloth Exporter] DB não encontrado em {DB_PATH}")
        return

    print(f"📡 Conectando na Máquina do Tempo O.S ({DB_PATH})...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Busca todas as mensagens na base, ordenadas por Data
    cursor.execute("""
        SELECT session_id, role, content 
        FROM chat_messages 
        ORDER BY session_id, created_at ASC
    """)
    rows = cursor.fetchall()
    
    # Agrupa por sessão (O contexto importa pro ShareGPT)
    sessions = {}
    for r in rows:
        sid = r['session_id']
        if sid not in sessions:
            sessions[sid] = []
        sessions[sid].append({"role": r['role'], "content": r['content']})
        
    conn.close()

    dataset_entries = []
    
    # Processando as sessões para Mapeamento Cíbrido (ShareGPT Format)
    for sid, messages in sessions.items():
        # ShareGPT precisa de no mínimo { human: ..., gpt: ... }
        # Transformaremos user -> human e assistant -> gpt
        
        current_conversation = []
        has_valuable_reflection = False
        
        for msg in messages:
            role = msg['role']
            content = msg['content'] or ""
            
            # Map Roles
            sharegpt_from = "human" if role == "user" else "gpt" if role == "assistant" else "system"
            
            if sharegpt_from == "system":
                # Opcional: ignorar system prompts padroes ou acoplar no primeiro "human"
                continue
                
            current_conversation.append({
                "from": sharegpt_from,
                "value": content
            })
            
            # Uma sessão só é "Ouro de Tolo" se o modelo realmente parou para refletir nela.
            if sharegpt_from == "gpt" and detect_thinking_tags(content):
                has_valuable_reflection = True
                
        # Validação: Só exporta cadeias de conversa inteiras onde houve Thought Chain
        if has_valuable_reflection and len(current_conversation) > 1:
            dataset_entries.append({"conversations": current_conversation})

    # Escrita final Jsonlines
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry in dataset_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            
    print(f"✅ [Distilação O.S] Safra Mestra Concluída!")
    print(f"📊 Foram envasadas {len(dataset_entries)} Sessões Perfeitas Ricas em <thinking>.")
    print(f"📦 Destino: {OUTPUT_PATH}")
    print(f"🚀 O SafeTensor Unsloth (Fase 5.5) já pode Engolir este Dataset.")

if __name__ == "__main__":
    export_to_sharegpt()
