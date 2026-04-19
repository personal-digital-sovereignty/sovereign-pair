-- ============================================================================
-- SOVEREIGN PAIR - CIBRID EPHEMERAL KNOWLEDGE SCHEMA
-- Modulo: Memoria temporal para noticias, publicacoes e artigos desestruturados
-- ============================================================================

-- Armazena o registro do documento volatil com metadados temporais rígidos
CREATE TABLE IF NOT EXISTS ephemeral_knowledge (
    id TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    domain TEXT NOT NULL,
    published_date DATETIME,
    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    title TEXT,
    content_raw TEXT
);

-- Armazena os Chunks (Textos Picotados)
CREATE TABLE IF NOT EXISTS ephemeral_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ephemeral_id TEXT NOT NULL,
    text_content TEXT NOT NULL,
    chunk_index INTEGER,
    metadata_json TEXT,
    FOREIGN KEY(ephemeral_id) REFERENCES ephemeral_knowledge(id) ON DELETE CASCADE
);

-- Tabela TurboQuantMSE (Camada de Embeddings Matemáticos Compressos)
-- Vetores comprimidos em 4-bit (10.6x menor pegada de memória)
CREATE TABLE IF NOT EXISTS vec_ephemeral_chunks (
    chunk_id INTEGER PRIMARY KEY,
    embedding BLOB NOT NULL,
    norm REAL NOT NULL,
    FOREIGN KEY(chunk_id) REFERENCES ephemeral_chunks(id) ON DELETE CASCADE
);
