"""
Report tests
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

def test_get_report_stats(auth_headers):
    """Test getting report statistics"""
    response = client.get("/api/v1/reports/stats", headers=auth_headers)
    assert response.status_code == 200
    assert "total_activities" in response.json()

def test_get_reports(auth_headers):
    """Test getting reports"""
    response = client.get("/api/v1/reports", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_individual_report(auth_headers):
    """Test getting individual report"""
    response = client.get("/api/v1/reports/individual/nonexistent-id", headers=auth_headers)
    assert response.status_code == 404

def test_get_individual_report_pdf(auth_headers):
    """Test downloading individual report PDF"""
    response = client.get("/api/v1/reports/individual/nonexistent-id/pdf", headers=auth_headers)
    assert response.status_code == 404

def test_get_group_report(auth_headers):
    """Test getting group report"""
    response = client.get("/api/v1/reports/group", headers=auth_headers)
    assert response.status_code == 200
    assert "html" in response.json()

def test_get_group_report_pdf(auth_headers):
    """Test downloading group report PDF"""
    response = client.get("/api/v1/reports/group/pdf", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_generate_report(auth_headers):
    """Test generating a new report"""
    response = client.post("/api/v1/reports/generate", 
                          json={
                              "type": "individual",
                              "title": "Test Report",
                              "description": "Test report description",
                              "params": {"activity_id": "test-id"}
                          }, 
                          headers=auth_headers)
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_report_templates(auth_headers):
    """Test getting report templates"""
    response = client.get("/api/v1/reports/templates", headers=auth_headers)
    assert response.status_code == 200
    assert "templates" in response.json()
