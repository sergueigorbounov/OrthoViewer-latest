import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, Mock

from app.main import app

client = TestClient(app)

# Mock data
MOCK_GENE_DATA = {
    "genes": [
        {
            "id": "gene1", 
            "name": "Gene 1", 
            "species_id": "sp1",
            "orthogroup_id": "OG0001",
            "go_terms": [
                {"id": "GO:0001", "name": "Term 1", "category": "Molecular Function"},
                {"id": "GO:0002", "name": "Term 2", "category": "Biological Process"}
            ]
        },
        {
            "id": "gene2", 
            "name": "Gene 2", 
            "species_id": "sp1",
            "orthogroup_id": "OG0002",
            "go_terms": []
        },
        {
            "id": "gene3", 
            "name": "Gene 3", 
            "species_id": "sp2",
            "orthogroup_id": "OG0001",
            "go_terms": [
                {"id": "GO:0003", "name": "Term 3", "category": "Cellular Component"}
            ]
        }
    ]
}

MOCK_ORTHOGROUP_DATA = {
    "orthogroups": [
        {"id": "OG0001", "name": "Orthogroup 1", "species": ["sp1", "sp2"]},
        {"id": "OG0002", "name": "Orthogroup 2", "species": ["sp1"]}
    ]
}

# Successful API calls
def test_get_all_genes_success():
    """Test successful retrieval of all genes."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_GENE_DATA
        response = client.get("/api/genes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["data"][0]["id"] == "gene1"
        assert data["data"][1]["id"] == "gene2"
        assert data["data"][2]["id"] == "gene3"

def test_get_gene_by_id_success():
    """Test successful retrieval of a gene by ID."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_GENE_DATA
        response = client.get("/api/gene/gene1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "gene1"
        assert data["data"]["name"] == "Gene 1"
        assert len(data["data"]["go_terms"]) == 2

def test_get_gene_go_terms_success():
    """Test successful retrieval of GO terms for a gene."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_GENE_DATA
        response = client.get("/api/gene/gene1/go_terms")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["gene_id"] == "gene1"
        assert len(data["terms"]) == 2
        assert data["terms"][0]["id"] == "GO:0001"
        assert data["terms"][1]["id"] == "GO:0002"

def test_get_orthogroup_genes_success():
    """Test successful retrieval of genes for an orthogroup."""
    with patch('app.main.load_mock_data') as mock_load:
        # First call for orthogroups, second call for genes
        mock_load.side_effect = [MOCK_ORTHOGROUP_DATA, MOCK_GENE_DATA]
        response = client.get("/api/orthogroup/OG0001/genes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["orthogroup_id"] == "OG0001"
        assert len(data["data"]) == 2
        assert data["data"][0]["id"] == "gene1"
        assert data["data"][1]["id"] == "gene3"

# Failed API calls
def test_get_gene_by_id_not_found():
    """Test retrieval of a non-existent gene."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_GENE_DATA
        response = client.get("/api/gene/non_existent")
        
        assert response.status_code == 200  # API still returns 200 but with success=False
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"]
        assert data["data"] is None

def test_get_gene_go_terms_not_found():
    """Test retrieval of GO terms for a gene without terms."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_GENE_DATA
        response = client.get("/api/gene/gene2/go_terms")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"]
        assert len(data["terms"]) == 0

def test_get_orthogroup_genes_orthogroup_not_found():
    """Test retrieval of genes for a non-existent orthogroup."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.side_effect = [MOCK_ORTHOGROUP_DATA, MOCK_GENE_DATA]
        response = client.get("/api/orthogroup/non_existent/genes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"]
        assert len(data["data"]) == 0

def test_get_genes_error():
    """Test handling of errors during gene retrieval."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.side_effect = Exception("Test error")
        response = client.get("/api/genes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to load gene data" in data["message"]
        assert len(data["data"]) == 0

# Fuzzy testing
def test_gene_route_special_characters():
    """Test gene routes with special characters in IDs."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.return_value = MOCK_GENE_DATA
        
        special_ids = ["gene%20with%20spaces", "gene+with+plus", "gene/with/slashes", "gene#with#hash"]
        
        for special_id in special_ids:
            response = client.get(f"/api/gene/{special_id}")
            # API should handle these gracefully
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert "success" in data