"""Complete authentication test script"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.services.user_service import UserService
from app.models.user import UserCreate, UserLogin
from app.core.security import verify_password, get_password_hash
from bson import ObjectId

async def test_database_connection():
    """Test database connection"""
    print("=" * 50)
    print("TEST 1: Database Connection")
    print("=" * 50)
    
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        await client.admin.command('ping')
        print("✅ Database connection successful")
        db = client[settings.DATABASE_NAME]
        
        # Check collections
        collections = await db.list_collection_names()
        print(f"✅ Collections: {collections}")
        
        # Check users count
        users_count = await db.users.count_documents({})
        print(f"✅ Users in database: {users_count}")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

async def test_security_functions():
    """Test password hashing and verification"""
    print("\n" + "=" * 50)
    print("TEST 2: Security Functions")
    print("=" * 50)
    
    try:
        test_password = "Test123!@#"
        hashed = get_password_hash(test_password)
        print(f"✅ Password hashed: {hashed[:50]}...")
        
        is_valid = verify_password(test_password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
        is_invalid = verify_password("wrong", hashed)
        print(f"✅ Wrong password rejected: {not is_invalid}")
        
        return True
    except Exception as e:
        print(f"❌ Security functions failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_creation():
    """Test user creation"""
    print("\n" + "=" * 50)
    print("TEST 3: User Creation")
    print("=" * 50)
    
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        db = client[settings.DATABASE_NAME]
        user_service = UserService(db)
        
        # Create test user
        user_data = UserCreate(
            name="Test User",
            email="test@example.com",
            password="Test123!@#",
            confirm_password="Test123!@#",
            department="Computer Science",
            role="student",
            student_id="TEST001",
            year_of_study=3
        )
        
        user = await user_service.create_user(user_data)
        print(f"✅ User created successfully: {user.id}")
        print(f"   Name: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        
        # Check if user exists in database
        user_doc = await db.users.find_one({"_id": ObjectId(user.id)})
        if user_doc:
            print(f"✅ User exists in database")
            print(f"   Has password_hash: {'password_hash' in user_doc}")
        else:
            print("❌ User not found in database")
            return False
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ User creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_authentication():
    """Test user authentication"""
    print("\n" + "=" * 50)
    print("TEST 4: User Authentication")
    print("=" * 50)
    
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        db = client[settings.DATABASE_NAME]
        user_service = UserService(db)
        
        # Authenticate with correct credentials
        user = await user_service.authenticate_user("test@example.com", "Test123!@#")
        
        if user:
            print(f"✅ Authentication successful")
            print(f"   User ID: {user.id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
        else:
            print("❌ Authentication failed: user is None")
            return False
        
        # Try wrong password
        user_wrong = await user_service.authenticate_user("test@example.com", "WrongPass123!@#")
        if not user_wrong:
            print("✅ Wrong password correctly rejected")
        else:
            print("❌ Wrong password was accepted!")
            return False
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 50)
    print("CLEANUP: Removing test data")
    print("=" * 50)
    
    try:
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        db = client[settings.DATABASE_NAME]
        
        result = await db.users.delete_many({"email": "test@example.com"})
        print(f"✅ Removed {result.deleted_count} test user(s)")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("\n🚀 Starting Authentication System Test\n")
    
    results = []
    
    # Test 1: Database connection
    result1 = await test_database_connection()
    results.append(("Database Connection", result1))
    
    if not result1:
        print("\n❌ Database connection failed. Cannot continue tests.")
        return
    
    # Test 2: Security functions
    result2 = await test_security_functions()
    results.append(("Security Functions", result2))
    
    # Test 3: User creation
    result3 = await test_user_creation()
    results.append(("User Creation", result3))
    
    # Test 4: Authentication
    if result3:
        result4 = await test_user_authentication()
        results.append(("User Authentication", result4))
    
    # Cleanup
    await cleanup_test_data()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 50)
    
    all_passed = all(r for _, r in results)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

