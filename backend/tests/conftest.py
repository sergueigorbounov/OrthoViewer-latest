import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch

# Import your app
from app.main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'ORTHOFINDER_DATA_DIR': '/tmp/test_data',
        'CORS_ORIGINS': 'http://localhost:3000'
    }):
        yield

@pytest.fixture(scope="session")
def mock_biological_data():
    """Session-scoped biological test data"""
    return {
        "test_newick": "((At:0.1,Os:0.2):0.05,Zm:0.15);",
        "test_orthogroups": {
            'Orthogroup': ['OG0000001', 'OG0000002'],
            'At': ['AT1G01010,AT1G01020', 'AT2G01010'],
            'Os': ['OS01G0100100', 'OS02G0100100'],
            'Zm': ['ZM01G00010', '']
        },
        "test_species_mapping": {
            'At': 'Arabidopsis thaliana',
            'Os': 'Oryza sativa',
            'Zm': 'Zea mays'
        }
    }
