"""Test login with the actual credentials"""
import requests
import json

def test_login():
    """Test login with akashpatil@gmail.com"""
    url = "http://localhost:8000/api/v1/auth/login"
    
    data = {
        "email": "akashpatil@gmail.com",
        "password": "TestPassword123!@#",
        "remember_me": False
    }
    
    print("=" * 60)
    print("Testing Login")
    print("=" * 60)
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse:")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            result = response.json()
            print(f"Access Token: {result.get('access_token')[:50]}...")
            print(f"User: {result.get('user').get('name')}")
            print(f"Email: {result.get('user').get('email')}")
        elif response.status_code == 500:
            print("❌ 500 ERROR")
            print(response.text)
        else:
            result = response.json()
            print(json.dumps(result, indent=2))
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_login()

