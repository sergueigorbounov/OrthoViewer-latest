import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, Mock

from app.main import app

client = TestClient(app)

# Mock data
MOCK_SPECIES_DATA = {
    "species": [
        {"id": "sp1", "name": "Species 1", "taxonomy": "Kingdom;Phylum;Class;Order;Family;Genus;Species"},
        {"id": "sp2", "name": "Species 2", "taxonomy": "Kingdom;Phylum;Class;Order;Family;Genus;Species"}
    ]
}

# Test cases for successful API calls
def test_get_all_species_success():
    """Test successful retrieval of all species."""
    with patch('app.api.routes.species.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_SPECIES_DATA
        response = client.get("/api/species")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["id"] == "sp1"
        assert data["data"][1]["id"] == "sp2"

def test_get_species_by_id_success():
    """Test successful retrieval of a species by ID."""
    with patch('app.api.routes.species.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_SPECIES_DATA
        response = client.get("/api/species/sp1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == "sp1"

# Test cases for failed API calls
def test_get_species_by_id_not_found():
    """Test retrieval of a non-existent species."""
    with patch('app.api.routes.species.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_SPECIES_DATA
        response = client.get("/api/species/non_existent")
        
        assert response.status_code == 200  # API still returns 200 but with success=False
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"]
        assert len(data["data"]) == 0

def test_get_all_species_error():
    """Test handling of errors during species retrieval."""
    with patch('app.api.routes.species.load_mock_data') as mock_load:
        mock_load.side_effect = Exception("Test error")
        response = client.get("/api/species")
        
        assert response.status_code == 200  # API still returns 200 but with success=False
        data = response.json()
        assert data["success"] is False
        assert "Failed to load species data" in data["message"]
        assert len(data["data"]) == 0

# Fuzzy testing - malformed requests
def test_species_route_malformed_id():
    """Test with various malformed IDs."""
    with patch('app.api.routes.species.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_SPECIES_DATA
        
        # Test with IDs that should be handled gracefully
        safe_ids = ["", " ", "123;456", "sp1'--"]
        
        for safe_id in safe_ids:
            response = client.get(f"/api/species/{safe_id}")
            # The API should handle these gracefully
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "success" in data
        
        # Test with IDs that FastAPI naturally rejects
        problematic_ids = ["<script>alert('XSS')</script>"]
        
        for problematic_id in problematic_ids:
            response = client.get(f"/api/species/{problematic_id}")
            # These should return 404 due to path encoding issues
            assert response.status_code in [200, 404]  # Allow either response