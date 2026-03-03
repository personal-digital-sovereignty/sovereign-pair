import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.auth import get_current_user

client = TestClient(app)

def override_get_current_user():
    return "test_tenant_xyz"

app.dependency_overrides[get_current_user] = override_get_current_user

def test_vault_agenda_structure():
    """Garante que o endpoint da Agenda Temporal retorne a estrutura correta (Buckets)"""
    response = client.get("/v1/vault/agenda")
    assert response.status_code == 200
    data = response.json()
    
    # Expected Time Buckets
    buckets = ["today", "this_week", "last_week", "this_month", "this_year", "older"]
    for b in buckets:
        assert b in data
        assert "docs" in data[b]
        assert "tasks" in data[b]
        
def test_vault_graph_structure():
    """Garante que o Sovereign Cognitive Graph receba Nodes e Links corretos"""
    response = client.get("/v1/vault/graph")
    assert response.status_code == 200
    data = response.json()
    
    # D3 / ForceGraph syntax
    assert "nodes" in data
    assert "links" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["links"], list)
