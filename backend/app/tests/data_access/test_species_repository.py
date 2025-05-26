import pytest
from unittest.mock import patch, MagicMock
from app.data_access.species_repository import SpeciesRepository
from app.models.biological_models import Species


@pytest.fixture
def mock_species_data():
    return {
        "species": [
            {"id": "sp1", "name": "Species 1", "taxonomy": "Kingdom;Phylum;Class;Order;Family;Genus;Species"},
            {"id": "sp2", "name": "Species 2", "taxonomy": "Kingdom;Phylum;Class;Order;Family;Genus;Species"}
        ]
    }


@pytest.fixture
def repository():
    return SpeciesRepository()


@patch("app.data_access.mock_repository.load_mock_data")
def test_get_all_species(mock_load_data, repository, mock_species_data):
    """Test getting all species."""
    # Setup
    mock_load_data.return_value = mock_species_data
    
    # Execute
    species_list = repository.get_all()
    
    # Assert
    assert len(species_list) == 2
    assert isinstance(species_list[0], Species)
    assert species_list[0].id == "sp1"
    assert species_list[0].name == "Species 1"
    assert species_list[1].id == "sp2"
    assert species_list[1].name == "Species 2"


@patch("app.data_access.mock_repository.load_mock_data")
def test_get_species_by_id(mock_load_data, repository, mock_species_data):
    """Test getting a species by ID."""
    # Setup
    mock_load_data.return_value = mock_species_data
    
    # Execute
    species = repository.get_by_id("sp1")
    
    # Assert
    assert species is not None
    assert species.id == "sp1"
    assert species.name == "Species 1"


@patch("app.data_access.mock_repository.load_mock_data")
def test_get_species_by_id_not_found(mock_load_data, repository, mock_species_data):
    """Test getting a species by ID that doesn't exist."""
    # Setup
    mock_load_data.return_value = mock_species_data
    
    # Execute
    species = repository.get_by_id("non_existent_id")
    
    # Assert
    assert species is None


@patch("app.data_access.mock_repository.load_mock_data")
def test_get_species_by_name(mock_load_data, repository, mock_species_data):
    """Test getting a species by name."""
    # Setup
    mock_load_data.return_value = mock_species_data
    
    # Execute
    species = repository.get_species_by_name("Species 1")
    
    # Assert
    assert species is not None
    assert species.id == "sp1"
    assert species.name == "Species 1"