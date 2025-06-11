import pytest
import time
import json
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open, MagicMock
import os

from app.services.gene_search_service import GeneSearchService

# Generate a large dataset for performance testing
def generate_large_gene_dataset(size=10000):
    """Generate a large gene dataset for performance testing."""
    np.random.seed(42)  # For reproducibility
    
    # Generate random gene data
    genes = []
    for i in range(1, size + 1):
        gene = {
            "id": f"gene{i}",
            "name": f"Gene {i}",
            "species_id": f"sp{np.random.randint(1, 101)}",  # 100 different species
            "orthogroup_id": f"OG{np.random.randint(1, 1001):04d}",  # 1000 different orthogroups
            "go_terms": [
                {
                    "id": f"GO:{np.random.randint(1, 10000):07d}",
                    "name": f"Term {np.random.randint(1, 1000)}",
                    "category": np.random.choice(["Molecular Function", "Biological Process", "Cellular Component"])
                } for _ in range(np.random.randint(0, 5))  # 0-4 GO terms per gene
            ]
        }
        genes.append(gene)
    
    # Add some special case genes for testing
    special_genes = [
        {
            "id": "SPECIAL1",
            "name": "Special Gene 1",
            "species_id": "sp1",
            "orthogroup_id": "OG0001",
            "go_terms": []
        },
        {
            "id": "SPECIAL2",
            "name": "Special Gene 2",
            "species_id": "sp2",
            "orthogroup_id": "OG0002",
            "go_terms": []
        },
        {
            "id": "SPECIAL3",
            "name": "Special Gene 3",
            "species_id": "sp3",
            "orthogroup_id": "OG0003",
            "go_terms": []
        }
    ]
    genes.extend(special_genes)
    
    return {"genes": genes}

@pytest.fixture
def large_gene_service():
    """Create a gene search service with a large dataset."""
    # Generate large datasets
    gene_data = generate_large_gene_dataset(10000)
    
    # Create a mock for the service
    service = MagicMock(spec=GeneSearchService)
    
    # Create DataFrames from mock data
    genes_df = pd.DataFrame(gene_data["genes"])
    genes_df.set_index("id", inplace=True)
    
    # Set the DataFrames on the service
    service.genes_df = genes_df
    
    # Use the real methods from GeneSearchService bound to the service instance
    service.get_gene_by_id = lambda gene_id: GeneSearchService.get_gene_by_id(service, gene_id)
    service.get_genes_by_orthogroup = lambda orthogroup_id: GeneSearchService.get_genes_by_orthogroup(service, orthogroup_id)
    service.get_genes_by_species = lambda species_id: GeneSearchService.get_genes_by_species(service, species_id)
    service.search_genes = lambda query, limit=10: GeneSearchService.search_genes(service, query, limit)
    
    return service

def test_get_gene_by_id_performance(large_gene_service):
    """Test the performance of gene retrieval by ID."""
    # Test with multiple gene IDs
    gene_ids = ["gene1", "gene5000", "gene9999", "SPECIAL1", "nonexistent"]
    
    for gene_id in gene_ids:
        start_time = time.time()
        result = large_gene_service.get_gene_by_id(gene_id)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert that the lookup takes less than 50ms
        assert duration_ms < 50, f"Gene lookup for {gene_id} took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
        
        # Verify the result
        assert "success" in result
        if gene_id in ["gene1", "gene5000", "gene9999", "SPECIAL1"]:
            assert result["success"] is True
            assert result["data"] is not None
        else:
            assert result["success"] is False
            assert result["data"] is None

def test_get_genes_by_orthogroup_performance(large_gene_service):
    """Test the performance of gene retrieval by orthogroup."""
    # Test with multiple orthogroup IDs
    orthogroup_ids = ["OG0001", "OG0100", "OG0500", "nonexistent"]
    
    for og_id in orthogroup_ids:
        start_time = time.time()
        result = large_gene_service.get_genes_by_orthogroup(og_id)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert that the lookup takes less than 50ms
        assert duration_ms < 50, f"Orthogroup lookup for {og_id} took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
        
        # Verify the result
        assert "success" in result
        assert "data" in result
        assert "orthogroup_id" in result
        assert result["orthogroup_id"] == og_id

def test_search_genes_performance(large_gene_service):
    """Test the performance of gene searching."""
    # Test with multiple search queries
    queries = ["Gene", "Gene 1", "SPECIAL", "nonexistent"]
    
    for query in queries:
        start_time = time.time()
        result = large_gene_service.search_genes(query)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert that the search takes less than 50ms
        assert duration_ms < 50, f"Gene search for '{query}' took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
        
        # Verify the result
        assert "success" in result
        assert "data" in result
        assert "query" in result
        assert result["query"] == query

def test_consecutive_searches_performance(large_gene_service):
    """Test the performance of consecutive searches."""
    # Perform multiple consecutive searches
    operations = [
        ("get_gene_by_id", "gene1"),
        ("get_gene_by_id", "gene5000"),
        ("get_genes_by_orthogroup", "OG0001"),
        ("search_genes", "Gene"),
        ("get_gene_by_id", "SPECIAL1"),
        ("search_genes", "SPECIAL")
    ]
    
    total_duration = 0
    
    for op_type, param in operations:
        start_time = time.time()
        
        if op_type == "get_gene_by_id":
            result = large_gene_service.get_gene_by_id(param)
        elif op_type == "get_genes_by_orthogroup":
            result = large_gene_service.get_genes_by_orthogroup(param)
        elif op_type == "search_genes":
            result = large_gene_service.search_genes(param)
        
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        total_duration += duration_ms
        
        # Assert that each operation takes less than 50ms
        assert duration_ms < 50, f"{op_type} with param '{param}' took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
    
    # Assert that the average time is reasonable
    avg_duration = total_duration / len(operations)
    print(f"Average operation duration: {avg_duration:.2f}ms")
    assert avg_duration < 30, f"Average operation duration was {avg_duration:.2f}ms, which is higher than expected"