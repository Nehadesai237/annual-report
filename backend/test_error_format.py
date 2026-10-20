"""Test error response format"""
import requests
import json

def test_error_format():
    """Test what error format backend returns"""
    
    # Test login with wrong credentials
    response = requests.post('http://localhost:8000/api/v1/auth/login', json={
        'email': 'rajnandinidesai381@gmail.com',
        'password': 'wrong',
        'remember_me': False
    })
    
    print("Status:", response.status_code)
    print("\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print("\nResponse Body:")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    print("\nData structure:")
    print(f"  data = {repr(data)}")
    print(f"  type(data) = {type(data)}")
    if isinstance(data, dict):
        for key in data.keys():
            print(f"  data['{key}'] = {repr(data[key])}")
    
if __name__ == "__main__":
    test_error_format()

