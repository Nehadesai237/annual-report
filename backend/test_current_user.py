"""Test current login with 500 error"""
import requests
import json

# Test the exact same request the frontend is making
def test_login():
    email = "rajnandinidesai381@gmail.com"
    password = "testpassword123"
    
    print("Testing login endpoint...")
    print(f"Email: {email}")
    print(f"Password: {password[:10]}...")
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/login',
            json={
                'email': email,
                'password': password,
                'remember_me': False
            },
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print("\nFull Response:")
        print(json.dumps(response.json(), indent=2))
        
        return response
    except Exception as e:
        print(f"\nError: {str(e)}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Login Endpoint for 500 Error")
    print("=" * 60)
    test_login()

