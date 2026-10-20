"""
Admin tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def admin_headers():
    """Get admin authentication headers for tests"""
    # Register admin user
    client.post("/api/v1/auth/register", json={
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "password123",
        "department": "Administration",
        "role": "admin"
    })
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "password123"
    })
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_rejected_activities(admin_headers):
    """Test getting rejected activities"""
    response = client.get("/api/v1/admin/rejected", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_pending_activities(admin_headers):
    """Test getting pending activities"""
    response = client.get("/api/v1/admin/pending", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_admin_stats(admin_headers):
    """Test getting admin statistics"""
    response = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    assert "total_activities" in response.json()

def test_approve_activity(admin_headers):
    """Test approving an activity"""
    # This would need an existing rejected activity ID
    response = client.post("/api/v1/admin/approve/nonexistent-id", 
                         json={"comments": "Approved by admin"}, 
                         headers=admin_headers)
    assert response.status_code == 404

def test_discard_activity(admin_headers):
    """Test discarding an activity"""
    # This would need an existing rejected activity ID
    response = client.post("/api/v1/admin/discard/nonexistent-id", 
                          json={"comments": "Discarded by admin"}, 
                          headers=admin_headers)
    assert response.status_code == 404

def test_bulk_approve(admin_headers):
    """Test bulk approving activities"""
    response = client.post("/api/v1/admin/bulk-approve", 
                          json={"activity_ids": ["id1", "id2"]}, 
                          headers=admin_headers)
    assert response.status_code == 200
    assert "results" in response.json()

def test_bulk_discard(admin_headers):
    """Test bulk discarding activities"""
    response = client.post("/api/v1/admin/bulk-discard", 
                          json={"activity_ids": ["id1", "id2"]}, 
                          headers=admin_headers)
    assert response.status_code == 200
    assert "results" in response.json()
