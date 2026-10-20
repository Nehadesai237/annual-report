"""
Test login with detailed error reporting
"""
import requests
import json

# Test login with wrong credentials
url = "http://localhost:8000/api/v1/auth/login"
data = {
    "email": "test@example.com",
    "password": "wrongpassword",
    "remember_me": False
}

print("Testing login endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")
print()

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print()
    
    try:
        response_data = response.json()
        print("Response JSON:")
        print(json.dumps(response_data, indent=2))
    except:
        print("Response Text:")
        print(response.text)
        
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

