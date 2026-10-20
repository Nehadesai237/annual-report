"""Check user and fix if needed"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.user_service import UserService

async def check_user():
    """Check if user exists and can login"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    # Check user
    user_doc = await db.users.find_one({"email": "akashpatil@gmail.com"})
    
    if user_doc:
        print("✅ User found in database:")
        print(f"   Name: {user_doc.get('name')}")
        print(f"   Email: {user_doc.get('email')}")
        print(f"   Role: {user_doc.get('role')}")
        print(f"   Student ID: {user_doc.get('student_id')}")
        print(f"   Is Active: {user_doc.get('is_active')}")
        print(f"   Password Hash: {'password_hash' in user_doc}")
        
        # Try to login
        print("\n🔐 Testing login...")
        user_service = UserService(db)
        
        # Try different passwords
        passwords = ["TestPassword123!@#", "password", "Password123"]
        
        for pwd in passwords:
            try:
                user = await user_service.authenticate_user("akashpatil@gmail.com", pwd)
                if user:
                    print(f"✅ Login works with password: {pwd[:10]}...")
                else:
                    print(f"❌ Login failed with password: {pwd[:10]}...")
            except Exception as e:
                print(f"❌ Error with {pwd[:10]}... : {str(e)}")
    else:
        print("❌ User not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_user())

