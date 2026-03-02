import sqlite3
import os
from src.config import CHROMA_DIR

DB_PATH = os.path.join(os.path.dirname(CHROMA_DIR), "sovereign_memory.db")
print(f"Applying schema migration to {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE system_settings RENAME TO system_settings_old;")
    except sqlite3.OperationalError:
        print("Table already renamed to system_settings_old")
    
    # 1.5 Drop old indices to free up the names for the new table
    cursor.execute("DROP INDEX IF EXISTS ix_system_settings_id;")
    cursor.execute("DROP INDEX IF EXISTS ix_system_settings_setting_key;")
    cursor.execute("DROP INDEX IF EXISTS ix_system_settings_tenant_id;")
    
    # 2. Create new table matching the exact definition in models.py (no UNIQUE on setting_key)
    cursor.execute("""
    CREATE TABLE system_settings (
        id INTEGER NOT NULL PRIMARY KEY,
        setting_key VARCHAR(100) NOT NULL,
        setting_value TEXT,
        tenant_id VARCHAR(50) NOT NULL DEFAULT 'default',
        updated_at DATETIME
    );
    """)
    
    # 3. Create indices
    cursor.execute("CREATE INDEX ix_system_settings_id ON system_settings (id);")
    cursor.execute("CREATE INDEX ix_system_settings_setting_key ON system_settings (setting_key);")
    cursor.execute("CREATE INDEX ix_system_settings_tenant_id ON system_settings (tenant_id);")

    # 4. Copy data over, ensuring we don't violate anything (though there are no constraints now)
    cursor.execute("""
    INSERT INTO system_settings (id, setting_key, setting_value, tenant_id, updated_at)
    SELECT id, setting_key, setting_value, tenant_id, updated_at FROM system_settings_old;
    """)
    
    # 5. Drop old table
    cursor.execute("DROP TABLE system_settings_old;")
    
    conn.commit()
    conn.close()
    print("Migration complete! UNIQUE constraint removed.")
except Exception as e:
    print("Migration failed:", e)
