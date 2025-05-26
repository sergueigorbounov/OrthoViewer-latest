import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, Mock

from app.main import app

client = TestClient(app)

# Mock data
MOCK_ORTHOGROUP_DATA = {
    "orthogroups": [
        {"id": "OG0001", "name": "Orthogroup 1", "species": ["sp1", "sp2"], "gene_count": 5},
        {"id": "OG0002", "name": "Orthogroup 2", "species": ["sp1"], "gene_count": 2},
        {"id": "OG0003", "name": "Orthogroup 3", "species": ["sp2", "sp3"], "gene_count": 3}
    ]
}

# Successful API calls
def test_get_all_orthogroups_success():
    """Test successful retrieval of all orthogroups."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_ORTHOGROUP_DATA
        response = client.get("/api/orthogroups")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["data"][0]["id"] == "OG0001"
        assert data["data"][1]["id"] == "OG0002"
        assert data["data"][2]["id"] == "OG0003"

def test_get_orthogroup_by_id_success():
    """Test successful retrieval of an orthogroup by ID."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_ORTHOGROUP_DATA
        response = client.get("/api/orthogroup/OG0001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "OG0001"
        assert data["data"][0]["species"] == ["sp1", "sp2"]

def test_get_species_orthogroups_success():
    """Test successful retrieval of orthogroups for a specific species."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_ORTHOGROUP_DATA
        response = client.get("/api/species/sp1/orthogroups")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["id"] == "OG0001"
        assert data["data"][1]["id"] == "OG0002"
        assert data["species_id"] == "sp1"

# Failed API calls
def test_get_orthogroup_by_id_not_found():
    """Test retrieval of a non-existent orthogroup."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_ORTHOGROUP_DATA
        response = client.get("/api/orthogroup/non_existent")
        
        assert response.status_code == 200  # API still returns 200 but with success=False
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"]
        assert len(data["data"]) == 0

def test_get_species_orthogroups_not_found():
    """Test retrieval of orthogroups for a non-existent species."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_ORTHOGROUP_DATA
        response = client.get("/api/species/non_existent/orthogroups")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True  # This is true because the API returns empty list, not an error
        assert len(data["data"]) == 0
        assert data["species_id"] == "non_existent"

def test_get_orthogroups_error():
    """Test handling of errors during orthogroup retrieval."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.side_effect = Exception("Test error")
        response = client.get("/api/orthogroups")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to load orthogroup data" in data["message"]
        assert len(data["data"]) == 0

# Fuzzy testing
def test_orthogroup_route_unusual_parameters():
    """Test with unusual parameters."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_ORTHOGROUP_DATA
        
        # Test with unusual query parameters
        response = client.get("/api/orthogroups?unusual=parameter")
        assert response.status_code == 200
        
        # Test with unusual headers
        response = client.get("/api/orthogroups", headers={"X-Unusual-Header": "value"})
        assert response.status_code == 200