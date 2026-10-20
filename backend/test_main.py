"""
Test FastAPI application that can run without MongoDB for testing
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from typing import Dict, Any

# Security scheme
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Annual Report Portal API - Test Mode",
    description="A test API for managing academic activities (no database)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for testing
fake_users_db: Dict[str, Dict[str, Any]] = {
    "test@example.com": {
        "id": "1",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "full_name": "Test User",
        "department": "Computer Science",
        "role": "student",
        "is_active": True
    }
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Annual Report Portal API - Test Mode",
        "version": "1.0.0",
        "docs": "/docs",
        "note": "Running in test mode without database"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "annual-report-api-test"}

# Auth endpoints for testing
@app.post("/api/v1/auth/register")
async def register_user(user_data: dict):
    """Register a new user (test mode)"""
    email = user_data.get("email")
    password = user_data.get("password")
    full_name = user_data.get("full_name", "")
    department = user_data.get("department", "")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    if email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create fake user
    user_id = str(len(fake_users_db) + 1)
    fake_users_db[email] = {
        "id": user_id,
        "email": email,
        "hashed_password": password,  # In real app, this would be hashed
        "full_name": full_name,
        "department": department,
        "role": "student",
        "is_active": True
    }
    
    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "email": email
    }

@app.post("/api/v1/auth/login")
async def login_user(credentials: dict):
    """Login user (test mode)"""
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # In test mode, accept any password
    if password != user.get("hashed_password") and password != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Return fake token
    return {
        "access_token": f"fake_token_{user['id']}",
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "department": user["department"],
            "role": user["role"]
        }
    }

@app.get("/api/v1/auth/me")
async def get_current_user():
    """Get current user info (test mode)"""
    return {
        "id": "1",
        "email": "test@example.com",
        "full_name": "Test User",
        "department": "Computer Science",
        "role": "student"
    }

if __name__ == "__main__":
    uvicorn.run(
        "test_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
