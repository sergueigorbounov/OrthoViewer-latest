import pytest
import json
import os
from unittest.mock import patch, mock_open

from app.main import load_mock_data

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
         patch('os.path.join', return_value='/mock/path/to/file.json'):
        
        result = load_mock_data("file.json")
        
        assert result == MOCK_JSON_DATA
        assert result["key1"] == "value1"
        assert result["key2"] == ["item1", "item2"]
        assert result["key3"]["nested_key"] == "nested_value"

def test_load_mock_data_file_not_found():
    """Test handling of file not found error."""
    with patch('builtins.open', side_effect=FileNotFoundError), \
         patch('os.path.join', return_value='/mock/path/to/nonexistent.json'):
        
        result = load_mock_data("nonexistent.json")
        
        # Function should return an empty dict on error
        assert result == {}

def test_load_mock_data_json_decode_error():
    """Test handling of JSON decode error."""
    with patch('builtins.open', mock_open(read_data="invalid json content")), \
         patch('os.path.join', return_value='/mock/path/to/invalid.json'):
        
        result = load_mock_data("invalid.json")
        
        # Function should return an empty dict on error
        assert result == {}

def test_load_mock_data_permission_error():
    """Test handling of permission error."""
    with patch('builtins.open', side_effect=PermissionError), \
         patch('os.path.join', return_value='/mock/path/to/protected.json'):
        
        result = load_mock_data("protected.json")
        
        # Function should return an empty dict on error
        assert result == {}