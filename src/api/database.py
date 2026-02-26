from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from config import CHROMA_DIR # O banco SQLite vai morar na pasta do banco vetorial

# O caminho físico do SQLite persistente
DB_PATH = os.path.join(os.path.dirname(CHROMA_DIR), "sovereign_memory.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Configuração Padrão do SQLite via SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
