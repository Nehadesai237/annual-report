"""
Database configuration and utilities
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Optional
from contextvars import ContextVar

# Use context variable to store the request
_request_var: ContextVar = ContextVar('request_var', default=None)

def set_request(request):
    """Set the current request"""
    _request_var.set(request)

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance from FastAPI app state"""
    request = _request_var.get()
    if request and hasattr(request.app.state, 'database'):
        return request.app.state.database
    
    # Fallback to creating a new connection if no app context
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client[settings.DATABASE_NAME]
