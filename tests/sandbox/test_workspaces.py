import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.api.database import SessionLocal
from src.api.models import SystemSettings
from src.api.routes import get_authorized_workspaces

db = SessionLocal()

print("--- RAW SETTINGS NA DB ---")
settings = db.query(SystemSettings).all()
for s in settings:
    if s.setting_key in ("default_intake_vault", "workspaces", "vault_path"):
        print(f"{s.setting_key}: '{s.setting_value}'")

print("\n--- PASTAS AUTORIZADAS (Validas e Existentes) ---")
res = get_authorized_workspaces(db, "default")
print(res)
db.close()
