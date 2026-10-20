"""
Database service for dependency injection
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database

# This is a simple re-export for dependency injection
# The actual database connection is managed in app.core.database
