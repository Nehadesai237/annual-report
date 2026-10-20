"""
Simple MongoDB connection test script
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mongodb_connection():
    """Test MongoDB connection"""
    
    # Try to load from config
    try:
        from app.core.config import settings
        mongodb_url = settings.MONGODB_URL
        database_name = settings.DATABASE_NAME
        print(f"📋 Using MongoDB URL: {mongodb_url}")
        print(f"📋 Database name: {database_name}")
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        mongodb_url = "mongodb://localhost:27017"
        database_name = "annual_report"
        print(f"📋 Using default URL: {mongodb_url}")
    
    try:
        print("\n🔄 Attempting to connect to MongoDB...")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # Get server info
        server_info = await client.server_info()
        print(f"\n📊 MongoDB Server Info:")
        print(f"   Version: {server_info.get('version', 'Unknown')}")
        print(f"   Server Type: {server_info.get('serviceName', 'mongod')}")
        
        # List databases
        databases = await client.list_database_names()
        print(f"\n📂 Available databases:")
        for db in databases:
            print(f"   - {db}")
        
        # Check if our database exists
        db = client[database_name]
        collections = await db.list_collection_names()
        
        if collections:
            print(f"\n📁 Collections in '{database_name}':")
            for col in collections:
                count = await db[col].count_documents({})
                print(f"   - {col}: {count} documents")
        else:
            print(f"\n📁 Database '{database_name}' exists but is empty")
        
        # Close connection
        client.close()
        print("\n✅ MongoDB connection test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to connect to MongoDB!")
        print(f"   Error: {str(e)}")
        print(f"\n🔧 Troubleshooting:")
        print("   1. Make sure MongoDB is installed")
        print("   2. Make sure MongoDB is running (mongod should be running)")
        print("   3. Try running: mongosh (to test manually)")
        print("   4. Check the connection URL in your .env file")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)
    success = asyncio.run(test_mongodb_connection())
    print("=" * 60)
    sys.exit(0 if success else 1)

