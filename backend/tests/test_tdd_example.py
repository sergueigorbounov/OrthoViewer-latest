import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_user_creation():
    """
    Test user creation workflow:
    1. Ensure user doesn't exist
    2. Create user
    3. Verify user was created
    """
    # Setup - ensure user doesn't exist
    username = "testuser"
    delete_response = client.delete(f"/api/users/{username}")
    
    # Step 1: Attempt to get non-existent user
    response = client.get(f"/api/users/{username}")
    assert response.status_code == 404
    
    # Step 2: Create user
    user_data = {
        "username": username,
        "email": "test@example.com",
        "full_name": "Test User"
    }
    create_response = client.post("/api/users/", json=user_data)
    assert create_response.status_code == 201
    assert create_response.json()["username"] == username
    
    # Step 3: Verify user exists
    get_response = client.get(f"/api/users/{username}")
    assert get_response.status_code == 200
    assert get_response.json()["username"] == username
    assert get_response.json()["email"] == user_data["email"]


def test_user_update():
    """
    Test user update workflow:
    1. Create user
    2. Update user
    3. Verify update was applied
    """
    # Setup - create user
    username = "updateuser"
    user_data = {
        "username": username,
        "email": "update@example.com",
        "full_name": "Update User"
    }
    client.post("/api/users/", json=user_data)
    
    # Step 1: Update user
    updated_data = {
        "email": "updated@example.com",
        "full_name": "Updated User"
    }
    update_response = client.patch(f"/api/users/{username}", json=updated_data)
    assert update_response.status_code == 200
    
    # Step 2: Verify update
    get_response = client.get(f"/api/users/{username}")
    assert get_response.status_code == 200
    assert get_response.json()["email"] == updated_data["email"]
    assert get_response.json()["full_name"] == updated_data["full_name"]