"""Test API endpoints for authentication"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """Test user registration"""
    print("\n" + "=" * 50)
    print("TEST: User Registration")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/register"
    
    data = {
        "name": "API Test User",
        "email": "apitest@example.com",
        "password": "Test123!@#",
        "confirm_password": "Test123!@#",
        "department": "Computer Science",
        "role": "student",
        "student_id": "API001",
        "year_of_study": 3
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Registration successful")
            result = response.json()
            print(f"   User ID: {result.get('id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Email: {result.get('email')}")
            return True
        else:
            print(f"❌ Registration failed")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_login():
    """Test user login"""
    print("\n" + "=" * 50)
    print("TEST: User Login")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    
    data = {
        "email": "apitest@example.com",
        "password": "Test123!@#",
        "remember_me": False
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful")
            result = response.json()
            print(f"   Access Token: {result.get('access_token')[:50]}...")
            print(f"   User: {result.get('user').get('name')}")
            return True
        else:
            print(f"❌ Login failed")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_wrong_password():
    """Test login with wrong password"""
    print("\n" + "=" * 50)
    print("TEST: Login with Wrong Password")
    print("=" * 50)
    
    url = f"{BASE_URL}/auth/login"
    
    data = {
        "email": "apitest@example.com",
        "password": "WrongPass123!@#",
        "remember_me": False
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Wrong password correctly rejected")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("\n🚀 Starting API Endpoint Tests\n")
    
    results = []
    
    # Test 1: Register
    result1 = test_register()
    results.append(("Registration", result1))
    
    # Test 2: Login
    if result1:
        result2 = test_login()
        results.append(("Login", result2))
        
        # Test 3: Wrong password
        result3 = test_wrong_password()
        results.append(("Wrong Password Rejection", result3))
    
    # Summary
    print("\n" + "=" * 50)
    print("API TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 50)
    
    all_passed = all(r for _, r in results)
    if all_passed:
        print("\n🎉 All API tests passed!")
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")

if __name__ == "__main__":
    import time
    print("Waiting for server to start...")
    time.sleep(3)  # Wait for server to start
    main()

