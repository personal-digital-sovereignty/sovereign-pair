import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import DATA_DIR

# Verifica se existe uma URL de banco fornecida pelo Docker/OS (.env)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Em ambientes de Nuvem (PostgreSQL)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(DATABASE_URL)
else:
    # Fallback para Desktop Local: SQLite Persistente ao lado do antigo ChromaDB
    DB_PATH = os.path.join(DATA_DIR, "sovereign_memory.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    # Ativa o modo WAL (Write-Ahead Logging) no SQLite
    # Isso elimina o problema de "Database is locked" quando o CLI e a UI rodam simultaneamente,
    # permitindo leituras e escritas concorrentes como num banco maior.
    from sqlalchemy import event
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        is_vec_loaded = False
        try:
            dbapi_connection.enable_load_extension(True)
            import sqlite_vec
            sqlite_vec.load(dbapi_connection)
            is_vec_loaded = True
        except AttributeError:
             pass # Python do OS compilado sem suporte local a Load Extension (Bypass temporário Fase B)
        except Exception:
            pass # Ignora falta da extensão C localmente (No ambiente Docker será instalado via requirements)
            
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        
        # Cria Tabela Virtual Vetorial apenas se o módulo C estiver injetado
        if is_vec_loaded:
            try:
                cursor.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS sovereign_vectors USING vec0(
                        chunk_id INTEGER PRIMARY KEY,
                        embedding float[1024]
                    );
                """)
            except Exception as e:
                import logging
                logging.warning(f"Erro ao criar Tabela Vetorial vec0: {e}")
        
        # Cria a tabela gêmea para segurar os Dados e Metadados brutos (Substituto do Chroma Storage)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sovereign_chunks (
                chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid_reference TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                text_content TEXT NOT NULL,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_workspace_paths():
    """
    Sovereign OS Router: Extrai a lista atômica de todos os Drives atrelados
    na Tabela `workspaces` do Banco Híbrido Cíbrido. 
    Usado pelo Motor RAG (LlamaIndex) para engolir múltiplos diretórios simultâneos.
    """
    from sqlalchemy.sql import text
    db = SessionLocal()
    try:
        # Puxa apenas a coluna `path` absolutizada
        result = db.execute(text("SELECT path FROM workspaces"))
        paths = [row[0] for row in result.fetchall()]
        return paths
    except Exception as e:
        print(f"🚨 Sovereign Memory Error: Falha ao extrair Workspaces O.S: {e}")
        return []
    finally:
        db.close()
