#!/usr/bin/env python3
"""
Sovereign Ticker Registry — Seed Script
========================================
Popula a tabela `ticker_registry` no banco SQLite do Sovereign Pair.

Fontes (em ordem):
  1. scripts/commodities_seed.json  — catálogo curado local (offline-safe)
  2. brapi.dev/api/available        — ~500 ativos B3 (requer internet)

Idempotente: usa INSERT OR IGNORE — pode ser re-executado sem duplicar dados.

Uso:
    python scripts/seed_ticker_registry.py [--db PATH] [--skip-brapi]
"""

import argparse
import json
import os
import sqlite3
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone

# ── Caminhos padrão ───────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR     = os.path.dirname(SCRIPT_DIR)
SEED_FILE    = os.path.join(SCRIPT_DIR, "commodities_seed.json")
DEFAULT_DB   = os.path.join(ROOT_DIR, "data", "sovereign_memory.db")
BRAPI_URL    = "https://brapi.dev/api/available"
BRAPI_TIMEOUT = 15  # segundos


# ── Utilidades ────────────────────────────────────────────────────────────────
def normalize_key(name: str) -> str:
    """Normaliza um nome para search_key: UPPERCASE, sem acento, espaço→underscore."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_str.upper().replace(" ", "_").replace("-", "_").replace(".", "_")


def find_db(explicit_path: str | None) -> str:
    if explicit_path:
        return explicit_path
    if os.path.exists(DEFAULT_DB):
        return DEFAULT_DB
    # Busca recursiva por sovereign_sensus.db a partir do ROOT_DIR
    for dirpath, _, files in os.walk(ROOT_DIR):
        for fname in files:
            if fname == "sovereign_memory.db":
                return os.path.join(dirpath, fname)
    raise FileNotFoundError(
        f"Banco sovereign_memory.db não encontrado. "
        f"Passe o caminho com --db ou inicie o servidor ao menos uma vez."
    )


# ── Seed a partir do JSON curado ──────────────────────────────────────────────
def seed_from_json(conn: sqlite3.Connection) -> int:
    if not os.path.exists(SEED_FILE):
        print(f"[WARN] {SEED_FILE} não encontrado — pulando seed local.")
        return 0

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        entries = json.load(f)

    inserted = 0
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()

    for entry in entries:
        sk = entry.get("search_key") or normalize_key(entry.get("yf_symbol", ""))
        cursor.execute(
            """
            INSERT OR IGNORE INTO ticker_registry
                (search_key, yf_symbol, full_name, sector, market,
                 query_type_hint, is_active, last_verified_at, source)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, 'seed')
            """,
            (
                sk,
                entry["yf_symbol"],
                entry.get("full_name", ""),
                entry.get("sector", ""),
                entry.get("market", "OTHER"),
                entry.get("query_type_hint", "price"),
                now,
            ),
        )
        if cursor.rowcount:
            inserted += 1

    conn.commit()
    print(f"[OK] Seed local: {inserted}/{len(entries)} entradas inseridas.")
    return inserted


# ── Seed a partir do brapi.dev ────────────────────────────────────────────────
def seed_from_brapi(conn: sqlite3.Connection) -> int:
    print(f"[...] Consultando brapi.dev ({BRAPI_URL}) …")
    try:
        req = urllib.request.Request(
            BRAPI_URL,
            headers={"User-Agent": "SovereignPair/1.2.x seed-script"},
        )
        with urllib.request.urlopen(req, timeout=BRAPI_TIMEOUT) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"[WARN] brapi.dev indisponível ({exc}) — seed B3 pulado.")
        return 0
    except Exception as exc:
        print(f"[WARN] Erro inesperado ao consultar brapi.dev: {exc}")
        return 0

    # Resposta esperada: {"indexes": [...], "stocks": [...]}
    stocks = raw.get("stocks", [])
    if not stocks:
        print("[WARN] brapi.dev retornou lista vazia de stocks.")
        return 0

    inserted = 0
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.cursor()

    for symbol in stocks:
        if not symbol or not isinstance(symbol, str):
            continue
        yf_sym = f"{symbol.upper()}.SA"
        sk = normalize_key(symbol)
        cursor.execute(
            """
            INSERT OR IGNORE INTO ticker_registry
                (search_key, yf_symbol, full_name, sector, market,
                 query_type_hint, is_active, last_verified_at, source)
            VALUES (?, ?, ?, '', 'B3', 'price', 1, ?, 'brapi')
            """,
            (sk, yf_sym, f"Ação B3: {symbol.upper()}", now),
        )
        if cursor.rowcount:
            inserted += 1

    conn.commit()
    print(f"[OK] brapi.dev: {inserted}/{len(stocks)} ativos B3 inseridos.")
    return inserted


# ── Migrate TICKER_MAP legado ─────────────────────────────────────────────────
TICKER_MAP_LEGACY = {
    "BRENT":          ("BZ=F",      "Petróleo Brent", "FUTURES"),
    "WTI":            ("CL=F",      "Petróleo WTI",   "FUTURES"),
    "GOLD":           ("GC=F",      "Ouro",           "FUTURES"),
    "SILVER":         ("SI=F",      "Prata",          "FUTURES"),
    "DOLAR":          ("BRL=X",     "Dólar/BRL",      "FX"),
    "USD":            ("BRL=X",     "Dólar/BRL",      "FX"),
    "EURO":           ("EURBRL=X",  "Euro/BRL",       "FX"),
    "PETROBRAS":      ("PETR4.SA",  "Petrobras PN",   "B3"),
    "NUBANK":         ("NU",        "NuBank",         "NYSE"),
    "VALE":           ("VALE3.SA",  "Vale",           "B3"),
    "ITAU":           ("ITUB4.SA",  "Itaú Unibanco",  "B3"),
    "BRADESCO":       ("BBDC4.SA",  "Bradesco",       "B3"),
    "BANCO_DO_BRASIL":("BBAS3.SA",  "Banco do Brasil","B3"),
    "AMBEV":          ("ABEV3.SA",  "Ambev",          "B3"),
    "MAGAZINE":       ("MGLU3.SA",  "Magazine Luiza", "B3"),
    "MAGALU":         ("MGLU3.SA",  "Magazine Luiza", "B3"),
    "WEG":            ("WEGE3.SA",  "WEG",            "B3"),
    "SUZANO":         ("SUZB3.SA",  "Suzano",         "B3"),
    "JBS":            ("JBSS3.SA",  "JBS",            "B3"),
    "ELETROBRAS":     ("ELET3.SA",  "Eletrobras",     "B3"),
    "LOCALIZA":       ("RENT3.SA",  "Localiza",       "B3"),
    "HAPVIDA":        ("HAPV3.SA",  "Hapvida",        "B3"),
    "SANTANDER":      ("SANB11.SA", "Santander BR",   "B3"),
}


def seed_from_legacy_map(conn: sqlite3.Connection) -> int:
    cursor = conn.cursor()
    inserted = 0
    now = datetime.now(timezone.utc).isoformat()
    for key, (sym, name, mkt) in TICKER_MAP_LEGACY.items():
        sk = normalize_key(key)
        cursor.execute(
            """
            INSERT OR IGNORE INTO ticker_registry
                (search_key, yf_symbol, full_name, sector, market,
                 query_type_hint, is_active, last_verified_at, source)
            VALUES (?, ?, ?, '', ?, 'price', 1, ?, 'seed')
            """,
            (sk, sym, name, mkt, now),
        )
        if cursor.rowcount:
            inserted += 1
    conn.commit()
    print(f"[OK] TICKER_MAP legado: {inserted}/{len(TICKER_MAP_LEGACY)} entradas migradas.")
    return inserted


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Sovereign Ticker Registry Seed")
    parser.add_argument("--db", default=None, help="Caminho para sovereign_memory.db")
    parser.add_argument("--skip-brapi", action="store_true", help="Pular sync com brapi.dev")
    args = parser.parse_args()

    try:
        db_path = find_db(args.db)
    except FileNotFoundError as exc:
        print(f"[ERRO] {exc}")
        sys.exit(1)

    print(f"[DB] Usando banco: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")

    # Garante que a tabela existe (caso o servidor ainda não tenha rodado a migration)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS ticker_registry (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            search_key       TEXT    NOT NULL UNIQUE,
            yf_symbol        TEXT    NOT NULL,
            full_name        TEXT    DEFAULT '',
            sector           TEXT    DEFAULT '',
            market           TEXT    NOT NULL DEFAULT 'B3',
            query_type_hint  TEXT    NOT NULL DEFAULT 'price',
            is_active        INTEGER NOT NULL DEFAULT 1,
            last_verified_at DATETIME,
            source           TEXT    NOT NULL DEFAULT 'seed'
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_ticker_search ON ticker_registry(search_key);
        CREATE        INDEX IF NOT EXISTS idx_ticker_symbol ON ticker_registry(yf_symbol);
    """)

    total = 0
    total += seed_from_legacy_map(conn)
    total += seed_from_json(conn)
    if not args.skip_brapi:
        total += seed_from_brapi(conn)

    # Resumo final
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ticker_registry")
    count = cursor.fetchone()[0]
    conn.close()

    print(f"\n[SUMMARY] {total} entradas novas adicionadas. Total no banco: {count} tickers.")
    print("[DONE] Sovereign Ticker Registry pronto.")


if __name__ == "__main__":
    main()
