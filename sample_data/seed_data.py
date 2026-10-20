#!/usr/bin/env python3
"""
Sample data seeding script for Annual Report Portal
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import random

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_database():
    """Seed the database with sample data"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    try:
        print("🌱 Seeding database with sample data...")
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        await db.users.delete_many({})
        await db.activities.delete_many({})
        await db.reports.delete_many({})
        await db.notifications.delete_many({})
        await db.audit_logs.delete_many({})
        
        # Create sample users
        print("👥 Creating sample users...")
        users = [
            {
                "name": "Admin User",
                "email": "admin@example.com",
                "password_hash": pwd_context.hash("password123"),
                "department": "Administration",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "name": "John Doe",
                "email": "student@example.com",
                "password_hash": pwd_context.hash("password123"),
                "department": "Computer Science",
                "role": "student",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=25),
                "updated_at": datetime.utcnow() - timedelta(days=25)
            },
            {
                "name": "Dr. Jane Smith",
                "email": "faculty@example.com",
                "password_hash": pwd_context.hash("password123"),
                "department": "Computer Science",
                "role": "faculty",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=20),
                "updated_at": datetime.utcnow() - timedelta(days=20)
            },
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "password_hash": pwd_context.hash("password123"),
                "department": "Mathematics",
                "role": "student",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=15),
                "updated_at": datetime.utcnow() - timedelta(days=15)
            },
            {
                "name": "Bob Wilson",
                "email": "bob@example.com",
                "password_hash": pwd_context.hash("password123"),
                "department": "Physics",
                "role": "student",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=10),
                "updated_at": datetime.utcnow() - timedelta(days=10)
            }
        ]
        
        user_results = await db.users.insert_many(users)
        user_ids = [str(user_id) for user_id in user_results.inserted_ids]
        
        # Create sample activities
        print("📝 Creating sample activities...")
        activities = []
        activity_types = ["social", "sports", "academic", "cultural", "technical"]
        statuses = ["pending", "accepted", "rejected"]
        
        for i in range(20):
            user_id = random.choice(user_ids)
            user = users[user_ids.index(user_id)]
            
            activity = {
                "user_id": user_id,
                "title": f"Sample Activity {i+1}",
                "description": f"This is a sample activity description for activity {i+1}. It demonstrates the functionality of the Annual Report Portal.",
                "type": random.choice(activity_types),
                "department": user["department"],
                "year": 2024,
                "images": [
                    {
                        "filename": f"sample_image_{i+1}.jpg",
                        "path": f"uploads/sample_image_{i+1}.jpg",
                        "verdict": random.choice(["normal", "abnormal"]),
                        "score": random.uniform(0.3, 0.9),
                        "ml_checked_at": datetime.utcnow() - timedelta(days=random.randint(1, 20))
                    }
                ],
                "status": random.choice(statuses),
                "ml_checked_at": datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "updated_at": datetime.utcnow() - timedelta(days=random.randint(1, 30))
            }
            
            if activity["status"] == "rejected":
                activity["admin_reviewed_at"] = datetime.utcnow() - timedelta(days=random.randint(1, 15))
                activity["admin_reviewed_by"] = user_ids[0]  # Admin user
                activity["admin_comments"] = "Activity rejected due to inappropriate content."
            
            activities.append(activity)
        
        await db.activities.insert_many(activities)
        
        # Create sample notifications
        print("🔔 Creating sample notifications...")
        notifications = []
        
        for user_id in user_ids[1:]:  # Skip admin user
            for i in range(random.randint(1, 5)):
                notification = {
                    "user_id": user_id,
                    "title": f"Sample Notification {i+1}",
                    "message": f"This is a sample notification for user {user_id}.",
                    "type": random.choice(["info", "success", "warning", "error"]),
                    "read": random.choice([True, False]),
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 10))
                }
                notifications.append(notification)
        
        await db.notifications.insert_many(notifications)
        
        # Create sample reports
        print("📊 Creating sample reports...")
        reports = []
        
        for i in range(5):
            report = {
                "type": random.choice(["individual", "group", "department", "yearly"]),
                "title": f"Sample Report {i+1}",
                "description": f"This is a sample report description for report {i+1}.",
                "generated_by": random.choice(user_ids),
                "params": {
                    "department": random.choice(["Computer Science", "Mathematics", "Physics"]),
                    "year": 2024,
                    "type": random.choice(activity_types)
                },
                "status": "completed",
                "file_path": f"reports/sample_report_{i+1}.pdf",
                "file_size": random.randint(100000, 1000000),
                "generated_at": datetime.utcnow() - timedelta(days=random.randint(1, 15)),
                "completed_at": datetime.utcnow() - timedelta(days=random.randint(1, 15))
            }
            reports.append(report)
        
        await db.reports.insert_many(reports)
        
        # Create sample audit logs
        print("📋 Creating sample audit logs...")
        audit_logs = []
        
        for i in range(10):
            log = {
                "user_id": random.choice(user_ids),
                "action": random.choice(["create_activity", "update_activity", "approve_activity", "reject_activity"]),
                "resource_type": "activity",
                "resource_id": f"activity_{i+1}",
                "details": f"Sample audit log entry {i+1}",
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 20))
            }
            audit_logs.append(log)
        
        await db.audit_logs.insert_many(audit_logs)
        
        print("✅ Database seeded successfully!")
        print(f"👥 Created {len(users)} users")
        print(f"📝 Created {len(activities)} activities")
        print(f"🔔 Created {len(notifications)} notifications")
        print(f"📊 Created {len(reports)} reports")
        print(f"📋 Created {len(audit_logs)} audit logs")
        
        print("\n🎯 Demo credentials:")
        print("Admin: admin@example.com / password123")
        print("Student: student@example.com / password123")
        print("Faculty: faculty@example.com / password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
