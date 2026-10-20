"""
Test login with a valid user to check if 500 error occurs
"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings
from app.services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def test_login():
    """Test login with a valid user"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # Check if test user exists
    test_user = await db.users.find_one({"email": "test@tkiet.edu.in"})
    if not test_user:
        print("Creating test user...")
        user_data = {
            "name": "Test User",
            "email": "test@tkiet.edu.in",
            "password_hash": pwd_context.hash("Test@123"),
            "department": "Computer Science",
            "role": "student",
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.users.insert_one(user_data)
        print("✅ Test user created")
    else:
        print("✅ Test user exists")
    
    # Try to authenticate
    print("\nTesting authentication...")
    try:
        user_service = UserService(db)
        user = await user_service.authenticate_user("test@tkiet.edu.in", "Test@123")
        if user:
            print(f"✅ Authentication successful!")
            print(f"   User: {user.name} ({user.email})")
            print(f"   Role: {user.role}")
        else:
            print("❌ Authentication failed - no user returned")
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_login())

