#!/usr/bin/env python3
"""
Database seeding script for Annual Report Portal
"""

import asyncio
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_database():
    """Seed the database with initial data"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    print("🌱 Starting database seeding...")
    
    try:
        # Create collections and indexes
        await create_indexes(db)
        
        # Seed users
        await seed_users(db)
        
        # Seed sample activities
        await seed_activities(db)
        
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        client.close()

async def create_indexes(db):
    """Create database indexes"""
    print("📊 Creating database indexes...")
    
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("student_id", unique=True, sparse=True)
    await db.users.create_index("department")
    await db.users.create_index("role")
    
    # Activities collection indexes
    await db.activities.create_index("user_id")
    await db.activities.create_index("department")
    await db.activities.create_index("status")
    await db.activities.create_index("created_at")
    await db.activities.create_index([("user_id", 1), ("created_at", -1)])
    
    print("✅ Indexes created successfully!")

async def seed_users(db):
    """Seed users data"""
    print("👥 Seeding users...")
    
    # Check if users already exist
    existing_users = await db.users.count_documents({})
    if existing_users > 0:
        print("⚠️  Users already exist, skipping user seeding")
        return
    
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
        {
            "name": "Amit Patel",
            "email": "amit.patel@tkiet.edu.in",
            "password_hash": pwd_context.hash("Student@123"),
            "department": "Information Technology",
            "role": "student",
            "student_id": "IT2024002",
            "phone": "+91 9876543212",
            "year_of_study": 2,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Sneha Singh",
            "email": "sneha.singh@tkiet.edu.in",
            "password_hash": pwd_context.hash("Student@123"),
            "department": "Electronics and Communication",
            "role": "student",
            "student_id": "EC2024003",
            "phone": "+91 9876543213",
            "year_of_study": 4,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "name": "Vikram Joshi",
            "email": "vikram.joshi@tkiet.edu.in",
            "password_hash": pwd_context.hash("Student@123"),
            "department": "Mechanical Engineering",
            "role": "student",
            "student_id": "ME2024004",
            "phone": "+91 9876543214",
            "year_of_study": 1,
            "is_active": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.users.insert_many(users_data)
    print(f"✅ Created {len(result.inserted_ids)} users")
    
    # Print login credentials
    print("\n🔑 Login Credentials:")
    print("=" * 50)
    print("Admin:")
    print("  Email: admin@tkiet.edu.in")
    print("  Password: Admin@123")
    print("\nFaculty:")
    print("  Email: rajesh.kumar@tkiet.edu.in")
    print("  Password: Faculty@123")
    print("\nStudents:")
    print("  Email: priya.sharma@tkiet.edu.in")
    print("  Password: Student@123")
    print("  (Same password for all students)")
    print("=" * 50)

async def seed_activities(db):
    """Seed sample activities"""
    print("📝 Seeding sample activities...")
    
    # Check if activities already exist
    existing_activities = await db.activities.count_documents({})
    if existing_activities > 0:
        print("⚠️  Activities already exist, skipping activity seeding")
        return
    
    # Get user IDs
    users = await db.users.find({}).to_list(length=None)
    user_map = {user["email"]: str(user["_id"]) for user in users}
    
    activities_data = [
        {
            "title": "Won First Prize in National Coding Competition",
            "description": "Secured first position in the National Coding Competition organized by ACM India. Solved complex algorithmic problems and demonstrated excellent problem-solving skills.",
            "type": "technical",
            "department": "Computer Science",
            "user_id": user_map["priya.sharma@tkiet.edu.in"],
            "status": "accepted",
            "year": 2024,
            "images": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "title": "Best Paper Award at International Conference",
            "description": "Received the Best Paper Award for research work on 'Machine Learning Applications in Healthcare' at the International Conference on AI and Healthcare.",
            "type": "academic",
            "department": "Computer Science",
            "user_id": user_map["priya.sharma@tkiet.edu.in"],
            "status": "accepted",
            "year": 2024,
            "images": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "title": "Cultural Festival Organizer",
            "description": "Successfully organized the annual cultural festival 'TechFest 2024' with over 500 participants. Coordinated various events and managed logistics efficiently.",
            "type": "cultural",
            "department": "Information Technology",
            "user_id": user_map["amit.patel@tkiet.edu.in"],
            "status": "accepted",
            "year": 2024,
            "images": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "title": "Cricket Team Captain",
            "description": "Led the college cricket team to victory in the inter-college tournament. Demonstrated leadership skills and team coordination.",
            "type": "sports",
            "department": "Electronics and Communication",
            "user_id": user_map["sneha.singh@tkiet.edu.in"],
            "status": "pending",
            "year": 2024,
            "images": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "title": "Community Service Initiative",
            "description": "Organized a community service program to teach computer basics to underprivileged children. Impacted over 100 children in the local community.",
            "type": "social",
            "department": "Mechanical Engineering",
            "user_id": user_map["vikram.joshi@tkiet.edu.in"],
            "status": "accepted",
            "year": 2024,
            "images": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = await db.activities.insert_many(activities_data)
    print(f"✅ Created {len(result.inserted_ids)} sample activities")

if __name__ == "__main__":
    asyncio.run(seed_database())