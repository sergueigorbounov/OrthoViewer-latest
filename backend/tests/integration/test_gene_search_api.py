import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the optimized service
from app.services.gene_search_service import GeneSearchService
# Import the FastAPI app
from app.main import app

client = TestClient(app)

# Mock responses for the GeneSearchService
MOCK_GENE_RESPONSE = {
    "success": True,
    "data": {
        "id": "gene1",
        "name": "Gene 1",
        "species_id": "sp1",
        "orthogroup_id": "OG0001",
        "go_terms": [
            {"id": "GO:0001", "name": "Term 1", "category": "Molecular Function"}
        ]
    }
}

MOCK_GENES_BY_ORTHOGROUP_RESPONSE = {
    "success": True,
    "data": [
        {
            "id": "gene1",
            "name": "Gene 1",
            "species_id": "sp1",
            "orthogroup_id": "OG0001"
        },
        {
            "id": "gene3",
            "name": "Gene 3",
            "species_id": "sp2",
            "orthogroup_id": "OG0001"
        }
    ],
    "orthogroup_id": "OG0001"
}

MOCK_SEARCH_RESPONSE = {
    "success": True,
    "data": [
        {
            "id": "gene1",
            "name": "Gene 1",
            "species_id": "sp1",
            "orthogroup_id": "OG0001"
        },
        {
            "id": "gene2",
            "name": "Gene 2",
            "species_id": "sp1",
            "orthogroup_id": "OG0002"
        }
    ],
    "query": "Gene"
}

# Patch the GeneSearchService for testing
@pytest.fixture
def mock_gene_service():
    with patch('app.api.genes.GeneSearchService', autospec=True) as MockService:
        # Configure the mock
        mock_service = MockService.return_value
        mock_service.get_gene_by_id.return_value = MOCK_GENE_RESPONSE
        mock_service.get_genes_by_orthogroup.return_value = MOCK_GENES_BY_ORTHOGROUP_RESPONSE
        mock_service.search_genes.return_value = MOCK_SEARCH_RESPONSE
        
        yield mock_service

# Test gene retrieval by ID
def test_get_gene_by_id_api(mock_gene_service):
    """Test the API endpoint for retrieving a gene by ID."""
    response = client.get("/api/gene/gene1")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == "gene1"
    assert data["data"]["name"] == "Gene 1"
    
    # Verify the service was called correctly
    mock_gene_service.get_gene_by_id.assert_called_once_with("gene1")

# Test gene retrieval by orthogroup
def test_get_genes_by_orthogroup_api(mock_gene_service):
    """Test the API endpoint for retrieving genes by orthogroup."""
    response = client.get("/api/orthogroup/OG0001/genes")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["id"] == "gene1"
    assert data["data"][1]["id"] == "gene3"
    assert data["orthogroup_id"] == "OG0001"
    
    # Verify the service was called correctly
    mock_gene_service.get_genes_by_orthogroup.assert_called_once_with("OG0001")

# Test gene search
def test_search_genes_api(mock_gene_service):
    """Test the API endpoint for searching genes."""
    response = client.get("/api/genes/search?query=Gene")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["id"] == "gene1"
    assert data["data"][1]["id"] == "gene2"
    assert data["query"] == "Gene"
    
    # Verify the service was called correctly
    mock_gene_service.search_genes.assert_called_once_with("Gene", 10)

# Test gene search with limit
def test_search_genes_with_limit_api(mock_gene_service):
    """Test the API endpoint for searching genes with a limit."""
    response = client.get("/api/genes/search?query=Gene&limit=5")
    
    assert response.status_code == 200
    
    # Verify the service was called correctly with the limit
    mock_gene_service.search_genes.assert_called_once_with("Gene", 5)

# Test performance
def test_gene_api_performance(mock_gene_service):
    """Test the performance of the gene API endpoints."""
    endpoints = [
        "/api/gene/gene1",
        "/api/orthogroup/OG0001/genes",
        "/api/genes/search?query=Gene"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert that the API response takes less than 50ms
        assert duration_ms < 50, f"API call to {endpoint} took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True