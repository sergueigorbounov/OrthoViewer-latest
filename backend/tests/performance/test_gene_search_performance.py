import pytest
import time
import json
import pandas as pd
from unittest.mock import patch, mock_open

from app.main import get_gene_by_id, app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test data
MOCK_GENE_DATA = {
    "genes": [
        {"id": f"gene{i}", "name": f"Gene {i}", "species_id": f"sp{i%3+1}", "orthogroup_id": f"OG000{i%5+1}"} 
        for i in range(1, 1001)  # 1000 genes
    ]
}

# Create a pandas DataFrame for more efficient searching
gene_df = pd.DataFrame(MOCK_GENE_DATA["genes"])
gene_df.set_index("id", inplace=True)

# Alternative implementation using pandas for faster lookup
def get_gene_by_id_pandas(gene_id: str):
    """Get gene details by ID using pandas for faster lookup."""
    try:
        if gene_id in gene_df.index:
            gene = gene_df.loc[gene_id].to_dict()
            return {
                "success": True,
                "data": gene
            }
        else:
            return {
                "success": False,
                "message": f"Gene with ID {gene_id} not found",
                "data": None
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load gene data: {str(e)}",
            "data": None
        }

# Test the performance of the original implementation
def test_original_gene_lookup_performance():
    """Test the performance of the original gene lookup implementation."""
    with patch('app.main.load_mock_data', return_value=MOCK_GENE_DATA):
        # Test with multiple gene IDs
        gene_ids = ["gene1", "gene500", "gene999", "nonexistent"]
        
        for gene_id in gene_ids:
            start_time = time.time()
            response = client.get(f"/api/gene/{gene_id}")
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            
            # Assert that the lookup takes less than 50ms
            assert duration_ms < 50, f"Gene lookup for {gene_id} took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert "success" in data

# Test the pandas implementation
def test_pandas_gene_lookup_performance():
    """Test the performance of the pandas-based gene lookup implementation."""
    gene_ids = ["gene1", "gene500", "gene999", "nonexistent"]
    
    for gene_id in gene_ids:
        start_time = time.time()
        result = get_gene_by_id_pandas(gene_id)
        end_time = time.time()
        
        duration_ms = (end_time - start_time) * 1000
        
        # Assert that the lookup takes less than 50ms
        assert duration_ms < 50, f"Pandas gene lookup for {gene_id} took {duration_ms:.2f}ms, which exceeds the 50ms threshold"
        
        # Verify the result
        assert "success" in result

# Compare the performance of both implementations
def test_compare_lookup_implementations():
    """Compare the performance of both gene lookup implementations."""
    with patch('app.main.load_mock_data', return_value=MOCK_GENE_DATA):
        gene_ids = ["gene1", "gene500", "gene999"]
        
        original_times = []
        pandas_times = []
        
        for gene_id in gene_ids:
            # Original implementation
            start_time = time.time()
            client.get(f"/api/gene/{gene_id}")
            original_times.append((time.time() - start_time) * 1000)
            
            # Pandas implementation
            start_time = time.time()
            get_gene_by_id_pandas(gene_id)
            pandas_times.append((time.time() - start_time) * 1000)
        
        # Calculate average times
        avg_original = sum(original_times) / len(original_times)
        avg_pandas = sum(pandas_times) / len(pandas_times)
        
        print(f"Average lookup time (original): {avg_original:.2f}ms")
        print(f"Average lookup time (pandas): {avg_pandas:.2f}ms")
        
        # Both should be under 50ms
        assert avg_original < 50
        assert avg_pandas < 50