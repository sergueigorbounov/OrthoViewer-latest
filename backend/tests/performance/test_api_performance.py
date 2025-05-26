import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint_performance():
    """Test the performance of the health endpoint."""
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    assert response.status_code == 200
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    assert response_time < 50, f"Response time was {response_time:.2f}ms, should be under 50ms"

def test_examples_endpoint_performance():
    """Test the performance of the examples endpoint."""
    start_time = time.time()
    response = client.get("/api/examples/1")
    end_time = time.time()
    
    assert response.status_code == 200
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    assert response_time < 50, f"Response time was {response_time:.2f}ms, should be under 50ms"

@pytest.mark.parametrize("endpoint", [
    "/health",
    "/api/examples",
    "/api/examples/1",
    "/api/status",
])
def test_multiple_endpoints_performance(endpoint):
    """Test the performance of multiple endpoints."""
    start_time = time.time()
    response = client.get(endpoint)
    end_time = time.time()
    
    assert response.status_code == 200
    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
    assert response_time < 50, f"{endpoint} response time was {response_time:.2f}ms, should be under 50ms"