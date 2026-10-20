"""
Authentication tests
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "department": "Computer Science",
        "role": "student"
    })
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == "test@example.com"

def test_register_duplicate_email():
    """Test registration with duplicate email"""
    # First registration
    client.post("/api/v1/auth/register", json={
        "name": "Test User 1",
        "email": "duplicate@example.com",
        "password": "password123",
        "department": "Computer Science",
        "role": "student"
    })
    
    # Second registration with same email
    response = client.post("/api/v1/auth/register", json={
        "name": "Test User 2",
        "email": "duplicate@example.com",
        "password": "password123",
        "department": "Mathematics",
        "role": "student"
    })
    assert response.status_code == 400

def test_login_user():
    """Test user login"""
    # Register user first
    client.post("/api/v1/auth/register", json={
        "name": "Login Test User",
        "email": "login@example.com",
        "password": "password123",
        "department": "Computer Science",
        "role": "student"
    })
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user():
    """Test getting current user info"""
    # Register and login
    client.post("/api/v1/auth/register", json={
        "name": "Current User Test",
        "email": "current@example.com",
        "password": "password123",
        "department": "Computer Science",
        "role": "student"
    })
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "current@example.com",
        "password": "password123"
    })
    
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "current@example.com"
