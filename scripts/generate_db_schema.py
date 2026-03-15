import os
import sys
from sqlalchemy import create_mock_engine

# Adiciona o diretorio base para resolver src.api.models
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, base_dir)

from src.api.models import Base

def dump_schema():
    out_file = os.path.join(base_dir, "data", "schema_0.4.1.sql")
    
    # Criamos um mock engine para interceptar comandos DDL ao invés de rodar no DB real
    def dump(sql, *multiparams, **params):
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(str(sql.compile(dialect=engine.dialect)).strip() + ";\n")
            
    engine = create_mock_engine('postgresql+psycopg2://', dump)
    
    # Prepara o arquivo limpo
    if os.path.exists(out_file):
        os.remove(out_file)
        
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("-- Sovereign Pair 0.4.1 - Database Schema Dump\n-- Autogerado via scripts/generate_db_schema.py\n\n")

    Base.metadata.create_all(engine, checkfirst=False)
    print(f"Schema exportado com sucesso para: {out_file}")

if __name__ == "__main__":
    dump_schema()
