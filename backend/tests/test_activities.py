"""
Activity tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Get authentication headers for tests"""
    # Register and login
    client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "department": "Computer Science",
        "role": "student"
    })
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_activity(auth_headers):
    """Test creating an activity"""
    # This would need actual file upload testing
    # For now, we'll test the endpoint structure
    response = client.post("/api/v1/activities", headers=auth_headers)
    # This will fail without proper form data, but tests the endpoint
    assert response.status_code in [400, 422]  # Bad request due to missing data

def test_get_activities(auth_headers):
    """Test getting activities"""
    response = client.get("/api/v1/activities", headers=auth_headers)
    assert response.status_code == 200
    assert "activities" in response.json()

def test_get_activities_with_filters(auth_headers):
    """Test getting activities with filters"""
    response = client.get("/api/v1/activities?type=academic&status=pending", headers=auth_headers)
    assert response.status_code == 200
    assert "activities" in response.json()

def test_get_activity_by_id(auth_headers):
    """Test getting a specific activity"""
    # This would need an existing activity ID
    response = client.get("/api/v1/activities/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404

def test_update_activity(auth_headers):
    """Test updating an activity"""
    # This would need an existing activity ID
    response = client.put("/api/v1/activities/nonexistent-id", 
                         json={"title": "Updated Title"}, 
                         headers=auth_headers)
    assert response.status_code == 404

def test_delete_activity(auth_headers):
    """Test deleting an activity"""
    # This would need an existing activity ID
    response = client.delete("/api/v1/activities/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404
