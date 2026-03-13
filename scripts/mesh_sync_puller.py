"""
SOVEREIGN MESH - THE CRON HUB SYNC (EDGE SCRIPT)
Executado periodicamente no PC Master (Edge Ryzen Local).

Missão: Contactar a Blue Collar Worker via IP Estático Tailscale (100.x.x.x), 
puxar documentos Scrapeados recentemente (Foraged) via RSYNC nativo do O.S. (ou API)
e anexar aos Embeddings locais usando The Mom.
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# IP Configurado do Oracle Cloud (Blue Collar)
BLUE_COLLAR_IP = os.getenv("TAILSCALE_BLUE_COLLAR_IP", "100.111.92.xx")
BLUE_COLLAR_USER = os.getenv("OCI_WORKER_USER", "ubuntu")
SYNC_VAULT_TARGET = os.getenv("SOVEREIGN_VAULT_ROOT", "/path/to/vault")

# Pasta receptora dentro do Vault
RAG_VAULT_DESTINATION = os.path.join(SYNC_VAULT_TARGET, "blue_collar_harvest")
os.makedirs(RAG_VAULT_DESTINATION, exist_ok=True)

def pull_harvested_rag_files():
    """Via SSH Key (Rsync), puxamos o banco SQLite cru do Worker."""
    print(f"[{datetime.utcnow().isoformat()}] Iniciando RAG Mesh Sync do Node: {BLUE_COLLAR_IP}...")
    
    # O script rsync extrai apenas do Docker Folder mapeado `infra/oci/worker_data/`
    REMOTE_PATH = f"{BLUE_COLLAR_USER}@{BLUE_COLLAR_IP}:~/sovereign-pair/infra/oci/worker_data/blue_collar.db"
    LOCAL_DB_CACHE = "./debug/blue_collar_temp.db"
    os.makedirs("./debug", exist_ok=True)
    
    try:
        # Puxa o DB atualizado com os novos RAGs forrageados
        res = subprocess.run(
            ["rsync", "-avz", "--progress", REMOTE_PATH, LOCAL_DB_CACHE],
            capture_output=True, text=True
        )
        if res.returncode != 0:
            print("[ERRO MESH SYNC] Falha de comunicação SSH/Tailscale com o Node OCI.")
            print(res.stderr)
            return
            
        print(">>> Banco de Mente Remotal Cíbrida (Blue Collar) sincronizado com sucesso!")
        parse_and_inject_to_vault(LOCAL_DB_CACHE)
        
    except Exception as e:
        print(f"[FATAL MESH CRASH] {e}")

def parse_and_inject_to_vault(sqlite_file: str):
    """Lê o banco remoto e materializa arquivos MD no God Mode (The Mom os observará imediatamente)"""
    import sqlite3
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()
    
    # Busca apenas pendentes
    try:
        cursor.execute("SELECT id, title, markdown_content, source_url FROM foraged_docs WHERE sync_status = 'PENDING'")
        rows = cursor.fetchall()
        
        if not rows:
            print(">>> Nenhuma nova Forrageada reportada pela Spider OCI.")
            return

        for row in rows:
            doc_id, title, markdown, source_url = row
            safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip()
            filename = f"spider_{safe_title[:50]}.md"
            filepath = os.path.join(RAG_VAULT_DESTINATION, filename)
            
            # Materiliza os arquivos no Sensus Vault local. The Mom irá rastreá-los e convertê-los em Vetores Cíbridos Imediatamente.
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)
                
            print(f"[THE MOM INBOX] Arquivo Gerado: {filename}")
            
            # Aqui deveriamos disparar uma flag de limpeza no OCI (API), 
            # Mas como o Worker é remoto e Passivo, daremos `sync_status = DONE` no local cache
            # Num sistema bi-direcional usaríamos SSH puro pra apagar lá na DB.
            
    except Exception as e:
         print(f"[ERRO PARSER] Banco corrompido ou indisponível: {e}")
    finally:
         conn.close()

if __name__ == "__main__":
    pull_harvested_rag_files()
