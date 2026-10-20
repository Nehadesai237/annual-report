"""Force reseed the database"""
import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def force_reseed():
    """Force reseed the database"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    print("🗑️  Dropping existing users and activities...")
    await db.users.delete_many({})
    await db.activities.delete_many({})
    
    print("👥 Creating users...")
    users_data = [
        {
            "name": "Admin User",
            "email": "admin@tkiet.edu.in",
            "password_hash": pwd_context.hash("Admin@123"),
            "department": "Administration",
            "role": "admin",
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Dr. Rajesh Kumar",
            "email": "rajesh.kumar@tkiet.edu.in",
            "password_hash": pwd_context.hash("Faculty@123"),
            "department": "Computer Science",
            "role": "faculty",
            "phone": "+91 9876543210",
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@tkiet.edu.in",
            "password_hash": pwd_context.hash("Student@123"),
            "department": "Computer Science",
            "role": "student",
            "student_id": "CS2024001",
            "phone": "+91 9876543211",
            "year_of_study": 3,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
    ]
    
    result = await db.users.insert_many(users_data)
    print(f"✅ Created {len(result.inserted_ids)} users")
    
    # Print login credentials
    print("\n🔑 Login Credentials:")
    print("=" * 50)
    print("Admin: admin@tkiet.edu.in / Admin@123")
    print("Faculty: rajesh.kumar@tkiet.edu.in / Faculty@123")
    print("Student: priya.sharma@tkiet.edu.in / Student@123")
    print("=" * 50)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(force_reseed())

