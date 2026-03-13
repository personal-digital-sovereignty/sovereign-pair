import sys
import os

# Força o diretório raiz do Sovereign-Pair ao PYTHONPATH antes dos testes
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)

# Override env settings BEFORE any src import
os.environ["DATABASE_URL"] = "sqlite:///./test_sensus.db"
os.environ["VAULT_DIR"] = "/tmp/sovereign_tests_vault"
os.environ["CHROMA_DIR"] = "/tmp/sovereign_tests_chroma"

import pytest  # noqa: E402
from src.api.database import engine, Base  # noqa: E402

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    os.makedirs("/tmp/sovereign_tests_vault", exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_sensus.db"):
        os.remove("./test_sensus.db")
