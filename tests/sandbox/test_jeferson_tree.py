import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.api.database import SessionLocal
from src.api.routes import get_authorized_workspaces
db = SessionLocal()
res = get_authorized_workspaces(db, "Jeferson")
print("Folders Resolvidas (ExpandUser + Abspath):", res)
db.close()
