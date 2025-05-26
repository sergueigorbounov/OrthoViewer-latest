import pytest
from fastapi.testclient import TestClient
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

MOCK_ORTHOGROUP_DATA = {
    "orthogroups": [
        {"id": "OG0001", "name": "Orthogroup 1", "species": ["sp1", "sp2"]},
        {"id": "OG0002", "name": "Orthogroup 2", "species": ["sp1"]}
    ]
}

MOCK_GENE_DATA = {
    "genes": [
        {
            "id": "gene1", 
            "name": "Gene 1", 
            "species_id": "sp1",
            "orthogroup_id": "OG0001",
            "orthogroups": ["OG0001"],
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
            "orthogroups": ["OG0002"],
            "go_terms": []
        },
        {
            "id": "gene3", 
            "name": "Gene 3", 
            "species_id": "sp2",
            "orthogroup_id": "OG0001",
            "orthogroups": ["OG0001"],
            "go_terms": [
                {"id": "GO:0003", "name": "Term 3", "category": "Cellular Component"}
            ]
        }
    ]
}

# Successful API calls
def test_get_dashboard_stats_success():
    """Test successful retrieval of dashboard statistics."""
    with patch('app.main.load_mock_data') as mock_load:
        # Mock to return different data based on the filename
        def mock_load_side_effect(filename):
            if filename == "species.json":
                return MOCK_SPECIES_DATA
            elif filename == "orthogroups.json":
                return MOCK_ORTHOGROUP_DATA
            elif filename == "genes.json":
                return MOCK_GENE_DATA
            return {}
        
        mock_load.side_effect = mock_load_side_effect
        
        response = client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        dashboard_data = data["data"]
        assert dashboard_data["speciesCount"] == 2
        assert dashboard_data["orthogroupCount"] == 2
        assert dashboard_data["geneCount"] == 3
        
        # Check species distribution
        assert len(dashboard_data["speciesDistribution"]) > 0
        
        # Check orthogroup connectivity
        assert len(dashboard_data["orthogroupConnectivity"]) > 0
        
        # Check GO term distribution
        assert "Molecular Function" in dashboard_data["goTermDistribution"]
        assert "Biological Process" in dashboard_data["goTermDistribution"]
        assert "Cellular Component" in dashboard_data["goTermDistribution"]

# Failed API calls
def test_get_dashboard_stats_error():
    """Test handling of errors during dashboard statistics retrieval."""
    with patch('app.main.load_mock_data') as mock_load:
        mock_load.side_effect = Exception("Test error")
        response = client.get("/api/dashboard/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Failed to generate dashboard stats" in data["message"]