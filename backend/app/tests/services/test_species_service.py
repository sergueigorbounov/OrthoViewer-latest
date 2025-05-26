import pytest
from unittest.mock import patch, MagicMock
from app.services.species_service import SpeciesService
from app.models.biological_models import Species, SpeciesResponse


@pytest.fixture
def service():
    return SpeciesService()


@patch("app.data_access.species_repository.SpeciesRepository.get_all")
def test_get_all_species_success(mock_get_all, service):
    """Test getting all species successfully."""
    # Setup
    mock_species = [
        Species(id="sp1", name="Species 1", taxonomy="Kingdom;Phylum;Class;Order;Family;Genus;Species"),
        Species(id="sp2", name="Species 2", taxonomy="Kingdom;Phylum;Class;Order;Family;Genus;Species")
    ]
    mock_get_all.return_value = mock_species
    
    # Execute
    response = service.get_all_species()
    
    # Assert
    assert isinstance(response, SpeciesResponse)
    assert response.success is True
    assert len(response.data) == 2
    assert response.data[0].id == "sp1"
    assert response.data[1].id == "sp2"


@patch("app.data_access.species_repository.SpeciesRepository.get_all")
def test_get_all_species_error(mock_get_all, service):
    """Test getting all species with an error."""
    # Setup
    mock_get_all.side_effect = Exception("Test error")
    
    # Execute
    response = service.get_all_species()
    
    # Assert
    assert isinstance(response, SpeciesResponse)
    assert response.success is False
    assert "Failed to load species data" in response.message
    assert len(response.data) == 0


@patch("app.data_access.species_repository.SpeciesRepository.get_by_id")
def test_get_species_by_id_success(mock_get_by_id, service):
    """Test getting a species by ID successfully."""
    # Setup
    mock_species = Species(id="sp1", name="Species 1", taxonomy="Kingdom;Phylum;Class;Order;Family;Genus;Species")
    mock_get_by_id.return_value = mock_species
    
    # Execute
    response = service.get_species_by_id("sp1")
    
    # Assert
    assert isinstance(response, SpeciesResponse)
    assert response.success is True
    assert len(response.data) == 1
    assert response.data[0].id == "sp1"
    assert response.data[0].name == "Species 1"


@patch("app.data_access.species_repository.SpeciesRepository.get_by_id")
def test_get_species_by_id_not_found(mock_get_by_id, service):
    """Test getting a species by ID that doesn't exist."""
    # Setup
    mock_get_by_id.return_value = None
    
    # Execute
    response = service.get_species_by_id("non_existent_id")
    
    # Assert
    assert isinstance(response, SpeciesResponse)
    assert response.success is False
    assert "not found" in response.message
    assert len(response.data) == 0


@patch("app.data_access.species_repository.SpeciesRepository.get_by_id")
def test_get_species_by_id_error(mock_get_by_id, service):
    """Test getting a species by ID with an error."""
    # Setup
    mock_get_by_id.side_effect = Exception("Test error")
    
    # Execute
    response = service.get_species_by_id("sp1")
    
    # Assert
    assert isinstance(response, SpeciesResponse)
    assert response.success is False
    assert "Failed to load species data" in response.message
    assert len(response.data) == 0