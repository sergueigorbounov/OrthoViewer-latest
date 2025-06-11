from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

MOCK_GENE_DATA = {
    'genes': [
        {'id': 'gene1', 'name': 'Gene 1', 'species_id': 'sp1', 'orthogroup_id': 'OG0001'},
        {'id': 'gene2', 'name': 'Gene 2', 'species_id': 'sp1', 'orthogroup_id': 'OG0002'},
        {'id': 'gene3', 'name': 'Gene 3', 'species_id': 'sp2', 'orthogroup_id': 'OG0001'}
    ]
}

client = TestClient(app)

print("Testing gene route with mock data...")
with patch('app.main.load_mock_data') as mock_load:
    mock_load.return_value = MOCK_GENE_DATA
    response = client.get('/api/genes')
    print('Status:', response.status_code)
    print('Response:', response.json())
    
    # Check what load_mock_data was called with
    print('Mock calls:', mock_load.call_args_list) 