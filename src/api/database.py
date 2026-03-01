import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.config import CHROMA_DIR

# Verifica se existe uma URL de banco fornecida pelo Docker/OS (.env)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Em ambientes de Nuvem (PostgreSQL)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(DATABASE_URL)
else:
    # Fallback para Desktop Local: SQLite Persistente ao lado do ChromaDB
    DB_PATH = os.path.join(os.path.dirname(CHROMA_DIR), "sovereign_memory.db")
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
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
