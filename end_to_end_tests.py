import unittest
import requests
import time
import os

# Base URLs for services
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8002")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:8001")
NGINX_URL = os.environ.get("NGINX_URL", "http://localhost:80")

class EndToEndTests(unittest.TestCase):
    """End-to-end tests for the complete application stack."""
    
    def test_backend_health(self):
        """Test that the backend health endpoint is working."""
        response = requests.get(f"{BACKEND_URL}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
    
    def test_frontend_loads(self):
        """Test that the frontend is accessible."""
        response = requests.get(FRONTEND_URL)
        self.assertEqual(response.status_code, 200)
    
    def test_nginx_proxy(self):
        """Test that the NGINX proxy is working for both frontend and backend."""
        # Test frontend through NGINX
        response = requests.get(NGINX_URL)
        self.assertEqual(response.status_code, 200)
        
        # Test backend API through NGINX
        response = requests.get(f"{NGINX_URL}/api/status")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("status" in response.json())
    
    def test_api_performance(self):
        """Test that API endpoints respond within the required timeframe (50ms)."""
        endpoints = [
            f"{BACKEND_URL}/health",
            f"{BACKEND_URL}/api/status",
            f"{BACKEND_URL}/api/examples"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            self.assertLess(response_time, 50, 
                            f"Response time for {endpoint} was {response_time:.2f}ms, should be under 50ms")
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()