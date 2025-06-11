import pytest
import pandas as pd
import json
from unittest.mock import patch, mock_open, MagicMock

from app.services.gene_search_service import GeneSearchService

# Mock data
MOCK_GENE_DATA = {
    "genes": [
        {
            "id": "gene1", 
            "name": "Gene 1", 
            "species_id": "sp1",
            "orthogroup_id": "OG0001",
            "go_terms": [
                {"id": "GO:0001", "name": "Term 1", "category": "Molecular Function"}
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
        },
        {
            "id": "ABCgene", 
            "name": "ABC Gene", 
            "species_id": "sp3",
            "orthogroup_id": "OG0003",
            "go_terms": []
        }
    ]
}

MOCK_ORTHOGROUP_DATA = {
    "orthogroups": [
        {"id": "OG0001", "name": "Orthogroup 1", "species": ["sp1", "sp2"]},
        {"id": "OG0002", "name": "Orthogroup 2", "species": ["sp1"]},
        {"id": "OG0003", "name": "Orthogroup 3", "species": ["sp3"]}
    ]
}

MOCK_SPECIES_DATA = {
    "species": [
        {"id": "sp1", "name": "Species 1"},
        {"id": "sp2", "name": "Species 2"},
        {"id": "sp3", "name": "Species 3"}
    ]
}

@pytest.fixture
def gene_search_service():
    """Create a gene search service with mock data."""
    # Create a mock for the service
    service = MagicMock(spec=GeneSearchService)
    
    # Create DataFrames from mock data
    genes_df = pd.DataFrame(MOCK_GENE_DATA["genes"])
    genes_df.set_index("id", inplace=True)
    
    orthogroups_df = pd.DataFrame(MOCK_ORTHOGROUP_DATA["orthogroups"])
    orthogroups_df.set_index("id", inplace=True)
    
    species_df = pd.DataFrame(MOCK_SPECIES_DATA["species"])
    species_df.set_index("id", inplace=True)
    
    # Set the DataFrames on the service
    service.genes_df = genes_df
    service.orthogroups_df = orthogroups_df
    service.species_df = species_df
    
    # Use the real methods from GeneSearchService bound to the service instance
    service.get_gene_by_id = lambda gene_id: GeneSearchService.get_gene_by_id(service, gene_id)
    service.get_genes_by_orthogroup = lambda orthogroup_id: GeneSearchService.get_genes_by_orthogroup(service, orthogroup_id)
    service.get_genes_by_species = lambda species_id: GeneSearchService.get_genes_by_species(service, species_id)
    service.search_genes = lambda query, limit=10: GeneSearchService.search_genes(service, query, limit)
    
    return service

def test_get_gene_by_id(gene_search_service):
    """Test getting a gene by ID."""
    # Test existing gene
    result = gene_search_service.get_gene_by_id("gene1")
    assert result["success"] is True
    assert result["data"]["name"] == "Gene 1"
    assert result["data"]["species_id"] == "sp1"
    
    # Test non-existent gene
    result = gene_search_service.get_gene_by_id("non_existent")
    assert result["success"] is False
    assert "not found" in result["message"]
    assert result["data"] is None

def test_get_genes_by_orthogroup(gene_search_service):
    """Test getting genes by orthogroup."""
    # Test existing orthogroup
    result = gene_search_service.get_genes_by_orthogroup("OG0001")
    assert result["success"] is True
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] in ["Gene 1", "Gene 3"]
    assert result["data"][1]["name"] in ["Gene 1", "Gene 3"]
    assert result["orthogroup_id"] == "OG0001"
    
    # Test non-existent orthogroup
    result = gene_search_service.get_genes_by_orthogroup("non_existent")
    assert result["success"] is False
    assert "not found" in result["message"]
    assert len(result["data"]) == 0
    assert result["orthogroup_id"] == "non_existent"

def test_get_genes_by_species(gene_search_service):
    """Test getting genes by species."""
    # Test existing species
    result = gene_search_service.get_genes_by_species("sp1")
    assert result["success"] is True
    assert len(result["data"]) == 2
    assert result["data"][0]["name"] in ["Gene 1", "Gene 2"]
    assert result["data"][1]["name"] in ["Gene 1", "Gene 2"]
    assert result["species_id"] == "sp1"
    
    # Test species with one gene
    result = gene_search_service.get_genes_by_species("sp3")
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["name"] == "ABC Gene"
    assert result["species_id"] == "sp3"
    
    # Test non-existent species
    result = gene_search_service.get_genes_by_species("non_existent")
    assert result["success"] is True  # Returns success but empty data
    assert len(result["data"]) == 0
    assert result["species_id"] == "non_existent"

def test_search_genes(gene_search_service):
    """Test searching for genes."""
    # Test search by name substring
    result = gene_search_service.search_genes("Gene")
    assert result["success"] is True
    assert len(result["data"]) == 3  # All genes except ABCgene
    
    # Test search by exact name
    result = gene_search_service.search_genes("Gene 1")
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["name"] == "Gene 1"
    
    # Test search by ID substring
    result = gene_search_service.search_genes("gene")
    assert result["success"] is True
    assert len(result["data"]) == 3  # gene1, gene2, gene3
    
    # Test search by exact ID
    result = gene_search_service.search_genes("gene1")
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == "gene1"
    
    # Test search with special ID format
    result = gene_search_service.search_genes("ABC")
    assert result["success"] is True
    assert len(result["data"]) == 1
    assert result["data"][0]["id"] == "ABCgene"
    
    # Test search with no results
    result = gene_search_service.search_genes("XYZ")
    assert result["success"] is True
    assert len(result["data"]) == 0
    
    # Test search with limit
    result = gene_search_service.search_genes("gene", limit=2)
    assert result["success"] is True
    assert len(result["data"]) == 2  # Only returns 2 results