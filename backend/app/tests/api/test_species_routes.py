import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main_clean import app
from app.models.biological_models import Species, SpeciesResponse

client = TestClient(app)


@patch("app.services.species_service.SpeciesService.get_all_species")
def test_get_species_route(mock_get_all):
    """Test the GET /api/species route."""
    # Setup
    mock_response = SpeciesResponse(
        success=True,
        data=[
            Species(id="sp1", name="Species 1", taxonomy="Kingdom;Phylum;Class;Order;Family;Genus;Species"),
            Species(id="sp2", name="Species 2", taxonomy="Kingdom;Phylum;Class;Order;Family;Genus;Species")
        ]
    )
    mock_get_all.return_value = mock_response
    
    # Execute
    response = client.get("/api/species")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["id"] == "sp1"
    assert data["data"][1]["id"] == "sp2"


@patch("app.services.species_service.SpeciesService.get_species_by_id")
def test_get_species_by_id_route(mock_get_by_id):
    """Test the GET /api/species/{species_id} route."""
    # Setup
    mock_response = SpeciesResponse(
        success=True,
        data=[
            Species(id="sp1", name="Species 1", taxonomy="Kingdom;Phylum;Class;Order;Family;Genus;Species")
        ]
    )
    mock_get_by_id.return_value = mock_response
    
    # Execute
    response = client.get("/api/species/sp1")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == "sp1"
    assert data["data"][0]["name"] == "Species 1"


@patch("app.services.species_service.SpeciesService.get_species_by_id")
def test_get_species_by_id_not_found_route(mock_get_by_id):
    """Test the GET /api/species/{species_id} route when species is not found."""
    # Setup
    mock_response = SpeciesResponse(
        success=False,
        message="Species with ID non_existent_id not found",
        data=[]
    )
    mock_get_by_id.return_value = mock_response
    
    # Execute
    response = client.get("/api/species/non_existent_id")
    
    # Assert
    assert response.status_code == 200  # Still returns 200 because it's a valid response
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"]
    assert len(data["data"]) == 0