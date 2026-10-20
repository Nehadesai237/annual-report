"""
FastAPI main application entry point for Annual Report Portal
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.database import get_database, set_request
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers

# Security scheme
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        print(f"🔄 Connecting to MongoDB at {settings.MONGODB_URL}...")
        app.state.db = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
        )
        await app.state.db.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Get database instance
        db = app.state.db[settings.DATABASE_NAME]
        app.state.database = db
        print(f"✅ Using database: {settings.DATABASE_NAME}")
        
    except Exception as e:
        print(f"❌ ERROR: Could not connect to MongoDB!")
        print(f"   URL: {settings.MONGODB_URL}")
        print(f"   Error: {str(e)}")
        print("\n🔧 Please ensure:")
        print("   1. MongoDB is installed and running")
        print("   2. Try running: python test_mongodb.py")
        print("   3. Check your .env file configuration")
        raise
    
    yield
    
    # Shutdown
    if app.state.db:
        app.state.db.close()
        print("✅ Disconnected from MongoDB")

# Create FastAPI app
app = FastAPI(
    title="Annual Report Portal API",
    description="A comprehensive API for managing academic activities and generating reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

@app.middleware("http")
async def set_request_context(request: Request, call_next):
    """Set request context for database access"""
    set_request(request)
    response = await call_next(request)
    return response

# CORS middleware - Allow all origins in development
# Note: When allow_credentials=True, we cannot use ["*"], so we list common origins
app.add_middleware(
    CORSMiddleware,
    # allows http://localhost, https://localhost, http://127.0.0.1, etc.
    # on ANY port (3000, 3001, etc.)
    allow_origin_regex='https?://.*', 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for uploads (images, certificates)
# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/certificates", exist_ok=True)

# Mount static file serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
