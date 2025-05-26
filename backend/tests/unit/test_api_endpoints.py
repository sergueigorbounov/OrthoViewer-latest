import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client):
    """Test the root endpoint returns basic info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "BioSemanticViz" in data["message"]

def test_status_endpoint(client):
    """Test the status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200

def test_api_status_endpoint(client):
    """Test the API status endpoint"""
    response = client.get("/api/status")
    assert response.status_code == 200
