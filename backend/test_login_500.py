"""Test login to see 500 error"""
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
        print(f"\nResponse Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test with the user's email
    email = "rajnandinidesai381@gmail.com"
    test_login(email, "anypassword")
