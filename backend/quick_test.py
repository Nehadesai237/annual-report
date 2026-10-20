"""Quick test for API authentication"""
import requests
import json
import time

def test_register_login():
    """Test registration and login via HTTP API"""
    base_url = "http://localhost:8000/api/v1"
    
    print("=" * 60)
    print("API AUTHENTICATION TEST")
    print("=" * 60)
    
    # Test 1: Register
    print("\n📝 Testing Registration...")
    register_data = {
        "name": "Quick Test User",
        "email": "quicktest@example.com",
        "password": "Test123!@#",
        "confirm_password": "Test123!@#",
        "department": "Computer Science",
        "role": "student",
        "student_id": "QT001",
        "year_of_study": 3
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/register",
            json=register_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            data = response.json()
            print(f"   User ID: {data.get('id')}")
            print(f"   Name: {data.get('name')}")
            print(f"   Email: {data.get('email')}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Login
    print("\n🔐 Testing Login...")
    login_data = {
        "email": "quicktest@example.com",
        "password": "Test123!@#",
        "remember_me": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"   Token: {data.get('access_token')[:40]}...")
            print(f"   User: {data.get('user').get('name')}")
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Wrong password
    print("\n🔒 Testing Wrong Password Rejection...")
    wrong_login_data = {
        "email": "quicktest@example.com",
        "password": "WrongPass123!@#",
        "remember_me": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=wrong_login_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Wrong password correctly rejected!")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print("\n⏳ Waiting for server to be ready...")
    time.sleep(5)
    test_register_login()

