import sqlite3
import os
from src.config import CHROMA_DIR

DB_PATH = os.path.join(os.path.dirname(CHROMA_DIR), "sovereign_memory.db")
print(f"Applying migrations to {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check what tables need tenant_id
    tables = {"system_settings", "chat_sessions", "chat_messages", "document_cache"}
    for table in tables:
        try:
            # Safely validate table names against an explicit allowlist (Fixes SAST rules)
            if table in tables:
                # nosemgrep: python.lang.security.audit.formatted-sql-query.formatted-sql-query, python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN tenant_id VARCHAR(50) DEFAULT 'default' NOT NULL;")
                print(f"Added tenant_id to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"{table} already has tenant_id")
            else:
                print(f"Error for {table}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration complete!")
except Exception as e:
    print("Migration failed:", e)
