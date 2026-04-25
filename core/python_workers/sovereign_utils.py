"""
Sovereign Pair - Core Python Utilities
(c) 2026 Sovereign Pair Project
"""

import os
import sys
import unicodedata

def normalize_key(name: str) -> str:
    """Normalizes a brand/equity name to upper ASCII snake_case."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_ = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_.upper().replace(" ", "_").replace("-", "_").replace(".", "_")

def get_db_path() -> str | None:
    """
    Locates sovereign_memory.db via standard env vars, XDG, macOS/Win appdata,
    with an ascending directory scan for local dev.
    """
    # 1. DATABASE_URL env var (prod / containers)
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        candidate = db_url.replace("sqlite:", "").split("?")[0]
        if os.path.exists(candidate):
            return candidate
            
    # 2. XDG_DATA_HOME (Linux custom)
    xdg = os.getenv("XDG_DATA_HOME", "")
    if xdg:
        candidate = os.path.join(xdg, "sovereign-pair", "data", "sovereign_memory.db")
        if os.path.exists(candidate):
            return candidate
            
    # 3. macOS ~/Library/Application Support
    if sys.platform == "darwin":
        candidate = os.path.join(os.path.expanduser("~"), "Library", "Application Support",
                                  "sovereign-pair", "data", "sovereign_memory.db")
        if os.path.exists(candidate):
            return candidate
            
    # 4. Windows %LOCALAPPDATA%
    local_app_data = os.getenv("LOCALAPPDATA", "")
    if local_app_data:
        candidate = os.path.join(local_app_data, "sovereign-pair", "data", "sovereign_memory.db")
        if os.path.exists(candidate):
            return candidate
            
    # 5. Linux ~/.local/share (XDG default)
    candidate = os.path.join(os.path.expanduser("~"), ".local", "share",
                              "sovereign-pair", "data", "sovereign_memory.db")
    if os.path.exists(candidate):
        return candidate
        
    # 6. Busca ascendente a partir do script (desenvolvimento local)
    cur = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(cur, "sovereign_memory.db")
        if os.path.exists(candidate):
            return candidate
        candidate2 = os.path.join(cur, "data", "sovereign_memory.db")
        if os.path.exists(candidate2):
            return candidate2
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
        
    return None
