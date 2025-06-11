import pytest
import json
import os
from unittest.mock import patch, mock_open

from app.api.biological_routes import load_mock_data

# Test data
MOCK_JSON_DATA = {
    "key1": "value1",
    "key2": ["item1", "item2"],
    "key3": {
        "nested_key": "nested_value"
    }
}

def test_load_mock_data_success():
    """Test successful loading of mock data."""
    # Mock the open function and file reading
    mock_json_string = json.dumps(MOCK_JSON_DATA)
    
    with patch('builtins.open', mock_open(read_data=mock_json_string)), \
         patch('os.path.exists', return_value=True):
        
        result = load_mock_data("file.json")
        
        assert result == MOCK_JSON_DATA
        assert result["key1"] == "value1"
        assert result["key2"] == ["item1", "item2"]
        assert result["key3"]["nested_key"] == "nested_value"

def test_load_mock_data_file_not_found():
    """Test handling of file not found error."""
    with patch('os.path.exists', return_value=False):
        
        result = load_mock_data("nonexistent.json")
        
        # Function should return an empty dict when no file found and no fallback
        assert result == {}

def test_load_mock_data_json_decode_error():
    """Test handling of JSON decode error."""
    with patch('builtins.open', mock_open(read_data="invalid json content")), \
         patch('os.path.exists', return_value=True):
        
        result = load_mock_data("invalid.json")
        
        # Function should return an empty dict on error
        assert result == {}

def test_load_mock_data_permission_error():
    """Test handling of permission error."""
    with patch('builtins.open', side_effect=PermissionError), \
         patch('os.path.exists', return_value=True):
        
        result = load_mock_data("protected.json")
        
        # Function should return an empty dict on error
        assert result == {}

def test_load_mock_data_fallback_genes():
    """Test fallback data for genes.json."""
    with patch('os.path.exists', return_value=False):
        
        result = load_mock_data("genes.json")
        
        # Should return fallback gene data
        assert result["genes"] is not None
        assert len(result["genes"]) == 3
        assert result["genes"][0]["id"] == "gene1"

def test_load_mock_data_fallback_species():
    """Test fallback data for species.json."""
    with patch('os.path.exists', return_value=False):
        
        result = load_mock_data("species.json")
        
        # Should return fallback species data
        assert result["species"] is not None
        assert len(result["species"]) == 2
        assert result["species"][0]["id"] == "sp1"

def test_load_mock_data_fallback_orthogroups():
    """Test fallback data for orthogroups.json."""
    with patch('os.path.exists', return_value=False):
        
        result = load_mock_data("orthogroups.json")
        
        # Should return fallback orthogroup data
        assert result["orthogroups"] is not None
        assert len(result["orthogroups"]) == 2
        assert result["orthogroups"][0]["id"] == "OG0001"