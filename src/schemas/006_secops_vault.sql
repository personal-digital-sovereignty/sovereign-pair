-- MIGRATION 006: UNIFIED SECOPS VAULT
-- Unifica as chaves fragmentadas em um único CRUD (API KEY, SSH KEY, PEM KEY, Certificados, URL, IP, Endpoints)

CREATE TABLE IF NOT EXISTS secops_vault (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    key_type TEXT NOT NULL,
    secret_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migra as chaves antigas de forma segura
INSERT OR IGNORE INTO secops_vault (id, name, key_type, secret_value, created_at, updated_at)
SELECT id, provider_name, 'API_KEY', api_key_value, created_at, updated_at FROM tenant_api_keys;
