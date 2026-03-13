"""
SOVEREIGN PAIR - BLUE COLLAR (OCI NODE)
Scrapper Autônomo para Forrageamento Web e Destilação.

Este Agente passivo desperta em horários pré-programados
ou via Webhooks do Tailscale. Ele varre a internet em busca
de tópicos determinados pelo Soberano, limpa o HTML e empacota
os dados em Markdown limpo no Banco SQLite Local. O Mestre
(`The Mom`) então suga este Banco via rsync/HTTP.
"""

import os
import time
import uuid
import schedule
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

# Configurações do Worker
WORKER_DATA_DIR = os.getenv("WORKER_DATA_DIR", "/app/data")
os.makedirs(WORKER_DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(WORKER_DATA_DIR, "blue_collar.db")

# Setup SQLAlchemy do SQLite Exclusivo do Worker
Base = declarative_base()

class ForagedDocument(Base):
    __tablename__ = 'foraged_docs'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_url = Column(String(512), unique=True, index=True)
    title = Column(String(255))
    theme = Column(String(100)) # e.g., 'Rust', 'A.I', 'Geopolitics'
    markdown_content = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    sync_status = Column(String(20), default="PENDING") # PENDING -> SYNCED (when Master pulls)

engine = create_engine(f"sqlite:///{DB_PATH}", isolation_level="AUTOCOMMIT")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def scrape_url(url: str) -> str:
    """Extrai texto limpo de uma URL erradicando os lixos HTML."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) SovereignPair/Spider'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Elimina tags não lexicais
        for script in soup(["script", "style", "nav", "footer", "aside", "header"]):
            script.extract()
            
        text = soup.get_text(separator='\n\n', strip=True)
        return text[:20000] # Cap para evitar OOM e engasgo do Embedder
    except Exception as e:
        print(f"[ERRO SCRAPING] {url}: {e}")
        return ""

def hunt_for_theme(theme_query: str, max_results: int = 3):
    """Varre o DDG por novos links sobre o Tema e os consome."""
    print(f"\n[{datetime.utcnow().isoformat()}] 🕷️ Spider acordou. Caçando tópico: '{theme_query}'")
    db = SessionLocal()
    try:
        results = DDGS().text(theme_query, max_results=max_results)
        
        for r in results:
            url = r.get('href')
            title = r.get('title')
            
            # Verifica se já não devoramos essa página
            exists = db.query(ForagedDocument).filter(ForagedDocument.source_url == url).first()
            if exists:
                print(f"[{theme_query}] Já asssimilado: {title[:40]}...")
                continue
                
            print(f"[{theme_query}] Devorando novo Link: {url}")
            content = scrape_url(url)
            
            if len(content) > 500: # Ignora scraps falhos (bloqueio cloudflare/js)
                doc = ForagedDocument(
                    source_url=url,
                    title=title,
                    theme=theme_query,
                    markdown_content=f"# {title}\n\n**Source:** {url}\n\n***\n\n{content}"
                )
                db.add(doc)
                db.commit()
                print(f"[{theme_query}] Salvo e aguardando Sync Mestre! ({len(content)} chars)")
            
            time.sleep(2) # Respeito ao DDG API rate limit
            
    except Exception as e:
        print(f"Falha na Caçada DDG: {e}")
    finally:
        db.close()

def job_pipeline():
    """O pipeline de caçadas pre-configuradas pelo Soberano."""
    # Estes tópicos poderão futuramente ser injetados por um endpoint do Blue Collar.
    topics = [
        "Rust Lang advanced concurrency patterns",
        "LangGraph Agentic workflows production",
        "Local LLM RAG multi-gpu strategies"
    ]
    
    for t in topics:
        hunt_for_theme(t, max_results=4)
        time.sleep(10)

if __name__ == "__main__":
    print(f"[{datetime.utcnow().isoformat()}] 🕷️ SOVEREIGN BLUE COLLAR - ON-LINE")
    print(f"Database persistente em: {DB_PATH}")
    
    # Roda a primeira bateria no ato do boot (Cíbrido Ativo)
    job_pipeline()
    
    # Agenda a caçada para ocorrer a cada 6 horas (Para não spammar a Cloud).
    schedule.every(6).hours.do(job_pipeline)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
