"""Test login with real user credentials"""
import requests
import json

def test_login(email, password):
    """Test login endpoint"""
    url = "http://localhost:8000/api/v1/auth/login"
    
    data = {
        "email": email,
        "password": password,
        "remember_me": False
    }
    
    print(f"\n{'='*60}")
    print(f"Testing Login for: {email}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Login successful!")
            return True
        else:
            print(f"\n❌ Login failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")
        return False

def test_user_exists(email):
    """Check if user exists in database"""
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    import asyncio
    
    async def check():
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        user = await db.users.find_one({"email": email})
        if user:
            print(f"✅ User found in database:")
            print(f"   Name: {user.get('name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Role: {user.get('role')}")
            print(f"   Has password_hash: {'password_hash' in user}")
            print(f"   Is Active: {user.get('is_active')}")
            client.close()
            return True
        else:
            print(f"❌ User not found in database")
            client.close()
            return False
    
    return asyncio.run(check())

if __name__ == "__main__":
    email = "rajnandinidesai381@gmail.com"
    
    print("\n" + "="*60)
    print("Testing User Login")
    print("="*60)
    
    # Check if user exists
    print("\n1. Checking if user exists...")
    exists = test_user_exists(email)
    
    if exists:
        # Try different passwords
        print("\n2. Testing login with password...")
        test_login(email, "password")
        test_login(email, "Password123")
        test_login(email, "Test123!@#")
    else:
        print("\nUser does not exist. You need to register first.")

