import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

os.environ["SENSUS_MODE"] = "enterprise"
os.environ["SOVEREIGN_MASTER_KEK"] = "0" * 64

from src.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

openapi = client.get("/openapi.json").json()
has_pomodoro = any("pomodoro" in path for path in openapi["paths"])
print("Test 1 - Enterprise Mode Active - Has Pomodoro Routes?", has_pomodoro)
assert not has_pomodoro, "Pomodoro routes should be AMPUTATED!"

print("Success Enterprise Check!")
