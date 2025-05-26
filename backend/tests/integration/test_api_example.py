import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_example():
    """Test GET /api/examples/{example_id} endpoint."""
    response = client.get("/api/examples/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "value" in data

def test_create_example():
    """Test POST /api/examples endpoint."""
    example_data = {
        "name": "New Example",
        "value": 42
    }
    response = client.post("/api/examples", json=example_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Example"
    assert data["value"] == 42
    assert "id" in data

def test_invalid_example():
    """Test validation errors are properly returned."""
    # Missing required field
    response = client.post("/api/examples", json={"name": "Invalid Example"})
    assert response.status_code == 422
    
    # Invalid value (negative)
    response = client.post("/api/examples", json={"name": "Invalid Example", "value": -5})
    assert response.status_code == 422