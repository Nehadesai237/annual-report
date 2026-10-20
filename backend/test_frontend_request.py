"""Test with exact frontend request format"""
import requests
import json

def test_frontend_format():
    """Test login with exact format frontend sends"""
    
    # Test the exact request the frontend makes
    data = {
        "email": "akashpatil@gmail.com",
        "password": "TestPassword123!@#",
        "remember_me": False
    }
    
    print("Testing with frontend request format...")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    url = "http://localhost:8000/api/v1/auth/login"
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 500:
            print("\n*** GOT 500 ERROR ***")
            print("Response:", response.text[:500])
        
        elif response.status_code == 401:
            result = response.json()
            print("\nResponse:")
            print(json.dumps(result, indent=2))
            
        elif response.status_code == 200:
            print("\n✅ SUCCESS!")
            result = response.json()
            print(f"Token: {result.get('access_token')[:50]}...")
            print(f"User: {result.get('user').get('name')}")
        
        return response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_frontend_format()

