from fastapi.testclient import TestClient
from src.main import app

def test_chat_error():
    print("Inicializando TestClient do FastAPI...")
    client = TestClient(app)  # noqa: F841
    
    # Criar um PING RÁPIDO para o endpoint
    print("Disparando TestClient via POST /v1/health")
    # Health check ou tentar bypassar auth
    # Aqui fazemos auth direto
    login_data = {"password": "Sovereign_Password_Not_Needed"} # Erro certo, mas ver se o Uvicorn ta vivo  # noqa: F841
    # Espera, precisamos fazer login real ou usar dependências fake.
    # Em vez disso, vou importar o build_chat_engine direto!
    
    print("Tentando importar motor LlamaIndex...")
    
test_chat_error()
