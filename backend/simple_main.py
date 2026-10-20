"""
Simple FastAPI backend for testing without MongoDB
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Security scheme
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="Annual Report Portal API",
    description="A comprehensive API for managing academic activities and generating reports",
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

# Simple in-memory storage
users_db = {
    "admin@example.com": {
        "id": "1",
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "password": "password123"  # In real app, this would be hashed
    }
}

# Pydantic models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    role: str = "student"
    department: Optional[str] = None
    student_id: Optional[str] = None
    phone: Optional[str] = None
    year_of_study: Optional[int] = None
    confirm_password: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[User] = None

# Simple authentication endpoints
@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login endpoint"""
    user = users_db.get(user_data.email)
    if not user or user["password"] != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Simple token (in real app, use JWT)
    token = f"fake_token_{user['id']}"
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user": User(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"]
        )
    }

@app.post("/api/v1/auth/register")
async def register(user_data: UserRegister):
    """Register endpoint"""
    if user_data.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password confirmation
    if user_data.confirm_password and user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    user_id = str(len(users_db) + 1)
    users_db[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "role": user_data.role,
        "department": user_data.department,
        "student_id": user_data.student_id,
        "phone": user_data.phone,
        "year_of_study": user_data.year_of_study,
        "password": user_data.password
    }
    
    return {"message": "User registered successfully", "user": {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "role": user_data.role
    }}

@app.get("/api/v1/auth/me", response_model=User)
async def get_current_user(token: str = Depends(security)):
    """Get current user"""
    # Simple token validation (in real app, decode JWT)
    if not token.credentials.startswith("fake_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = token.credentials.replace("fake_token_", "")
    for user in users_db.values():
        if user["id"] == user_id:
            return User(
                id=user["id"],
                email=user["email"],
                name=user["name"],
                role=user["role"]
            )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Annual Report Portal API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "annual-report-api"}

if __name__ == "__main__":
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
