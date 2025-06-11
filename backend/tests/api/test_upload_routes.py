import pytest
import io
import os
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open, MagicMock

from app.main import app

client = TestClient(app)

# Test file upload endpoints
def test_upload_file_success():
    """Test successful file upload."""
    with patch('builtins.open', mock_open()), \
         patch('os.path.getsize', return_value=1024), \
         patch('os.path.getctime', return_value=1234567890), \
         patch('uuid.uuid4', return_value="test-uuid"):
        
        # Create a test file
        test_file = io.BytesIO(b"Test file content")
        test_file.name = "test.ttl"
        
        response = client.post(
            "/api/upload",
            files={"file": (test_file.name, test_file, "application/octet-stream")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-uuid"
        assert data["metadata"]["filename"] == "test.ttl"
        assert data["metadata"]["filesize"] == 1024
        assert "nodes" in data
        assert "edges" in data

def test_upload_file_no_file():
    """Test file upload with no file."""
    response = client.post("/api/upload")
    assert response.status_code == 422  # Unprocessable Entity

def test_upload_file_empty_filename():
    """Test file upload with empty filename."""
    test_file = io.BytesIO(b"Test file content")
    test_file.name = ""
    
    response = client.post(
        "/api/upload",
        files={"file": (test_file.name, test_file, "application/octet-stream")}
    )
    
    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    data = response.json()
    assert "detail" in data

def test_upload_file_invalid_extension():
    """Test file upload with invalid file extension."""
    test_file = io.BytesIO(b"Test file content")
    test_file.name = "test.invalid"
    
    response = client.post(
        "/api/upload",
        files={"file": (test_file.name, test_file, "application/octet-stream")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "Invalid file format" in data["error"]

# Test visualization endpoints
def test_visualize_success():
    """Test successful visualization creation."""
    request_data = {
        "dataId": "test-id",
        "visualizationType": "network"
    }
    
    response = client.post("/api/visualize", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id"
    assert data["type"] == "network"
    assert "nodes" in data["data"]
    assert "edges" in data["data"]
    assert "metadata" in data

def test_visualize_missing_data_id():
    """Test visualization with missing data ID."""
    request_data = {
        "visualizationType": "network"
    }
    
    response = client.post("/api/visualize", json=request_data)
    
    assert response.status_code == 200  # API doesn't validate required fields
    data = response.json()
    assert data["id"] is None

# Test analyze endpoints
def test_analyze_success():
    """Test successful data analysis."""
    request_data = {
        "dataId": "test-id",
        "analysisType": "basic"
    }
    
    response = client.post("/api/analyze", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id"
    assert data["type"] == "basic"
    assert "results" in data
    assert "summary" in data["results"]
    assert "metrics" in data["results"]
    assert "patterns" in data["results"]

def test_analyze_custom_type():
    """Test analysis with custom analysis type."""
    request_data = {
        "dataId": "test-id",
        "analysisType": "custom"
    }
    
    response = client.post("/api/analyze", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-id"
    assert data["type"] == "custom"