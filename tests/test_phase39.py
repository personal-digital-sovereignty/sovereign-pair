import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.auth import get_current_user

client = TestClient(app)

def override_get_current_user():
    return "test_tenant_xyz"

app.dependency_overrides[get_current_user] = override_get_current_user

# Vamos criar uma variável global (ou encapsular) para guardar o ID criado
created_project_id = None

def test_create_project():
    """Testa a criação de um Projeto (The God Mode Cockpit - Phase 39)."""
    global created_project_id
    payload = {
        "name": "Integration Test Project",
        "purpose": "A test project for CI",
        "traction_status": "Ideation",
        "next_action": "Run pytest",
        "energy_level": "High",
        "progress_percent": 0,
        "friction_radar": None,
        "links": [
            {"url": "https://pytest.org", "label": "Pytest Docs"}
        ]
    }
    response = client.post("/v1/projects", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Assert fields
    assert data["name"] == payload["name"]
    assert data["traction_status"] == payload["traction_status"]
    assert len(data["links"]) == 1
    assert data["links"][0]["url"] == "https://pytest.org"
    
    created_project_id = data["id"]
    assert created_project_id is not None

def test_list_projects():
    """Testa se o Radar de Ação consegue ler o projeto criado."""
    response = client.get("/v1/projects")
    assert response.status_code == 200
    data = response.json()
    
    # Deve ser uma lista
    assert isinstance(data, list)
    # E nosso projeto mock deve estar nela
    found = any(p["id"] == created_project_id for p in data)
    assert found is True

def test_update_project():
    """Testa uma atualização atômica de status do projeto."""
    payload = {
        "traction_status": "Flowing",
        "progress_percent": 25,
        "next_action": "Complete test suite"
    }
    response = client.put(f"/v1/projects/{created_project_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["traction_status"] == "Flowing"
    assert data["progress_percent"] == 25
    assert data["next_action"] == "Complete test suite"
    assert data["name"] == "Integration Test Project"  # Deve manter o nome antigo

def test_add_project_log():
    """Testa a inserção de um Diário de Bordo no projeto."""
    payload = {
        "content": "Acabei de realizar 25% do setup do BD de teste."
    }
    response = client.post(f"/v1/projects/{created_project_id}/log", json=payload)
    assert response.status_code == 200
    
    # Valida se agora a listagem master devolve o log no join
    get_res = client.get("/v1/projects")
    data = get_res.json()
    proj = next(p for p in data if p["id"] == created_project_id)
    assert len(proj["logs"]) == 1
    assert proj["logs"][0]["content"] == payload["content"]

def test_delete_project():
    """Limpa o ambiente destruindo fisicamente o Projeto de Teste."""
    response = client.delete(f"/v1/projects/{created_project_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Garante que não está mais lá
    get_res = client.get("/v1/projects")
    data = get_res.json()
    found = any(p["id"] == created_project_id for p in data)
    assert found is False
