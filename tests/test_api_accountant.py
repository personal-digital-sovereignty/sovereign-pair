from fastapi.testclient import TestClient
from src.api.main import app
from src.api.auth import get_current_user

# Setup TestClient with mock Auth
client = TestClient(app)

def override_get_current_user():
    return "test_tenant_xyz"

app.dependency_overrides[get_current_user] = override_get_current_user

def test_evaluate_table_api_success():
    """Testa se a API responde corretamente com os valores computados."""
    payload = {
        "cells": {
            "A1": "100",
            "B1": "50",
            "C1": "=A1+B1"
        },
        "deleted_column": None
    }
    
    # Executa mock HTTP POST routeando pro The Accountant
    response = client.post("/v1/vault/table/evaluate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Backend The Accountant deve ter resolvido:
    assert data["results"]["A1"] == "100.0"
    assert data["results"]["B1"] == "50.0" 
    assert data["results"]["C1"] == "150.0"
    assert len(data["errors"]) == 0

def test_evaluate_table_api_circular_ref():
    """Testa se a API serializa erros matemáticos (Circular Refs) nas respostas de erro."""
    payload = {
        "cells": {
            "A1": "=B1",
            "B1": "=A1"
        },
        "deleted_column": None
    }
    
    response = client.post("/v1/vault/table/evaluate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["results"]["A1"] == "#CIRCULAR_REF!"
    assert data["errors"]["A1"] == "#CIRCULAR_REF!"
    assert data["errors"]["B1"] == "#CIRCULAR_REF!"

def test_evaluate_table_api_deletion_cascade():
    """Testa se a API aplica a deleção de coluna (deleted_column=B) em cascata no JSON de Resposta."""
    payload = {
        "cells": {
            "A1": "10",
            "B1": "20",
            "C1": "=A1+B1", # Ref que VAI quebrar quando B sumir
            "D1": "=C1+100" # Ref downstream que vai quebrar via cascade indireto do DAG
        },
        "deleted_column": "B"
    }
    
    response = client.post("/v1/vault/table/evaluate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # O Back-end informou que ocorreram refs inválidas
    assert data["results"]["C1"] == "#REF!"
    assert data["errors"]["C1"] == "#REF!"
    
    assert data["results"]["D1"] == "#REF!"
    assert data["errors"]["D1"] == "#REF!"
