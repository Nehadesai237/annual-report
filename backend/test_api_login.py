"""
Test the login API endpoint
"""
import requests
import json

# Test credentials
data = {
    "email": "test@tkiet.edu.in",
    "password": "Test@123",
    "remember_me": False
}

print("Testing login API endpoint...")
print(f"POST http://localhost:8000/api/v1/auth/login")
print(f"Data: {json.dumps(data, indent=2)}")
print()

try:
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        print("✅ Login successful!")
        try:
            response_data = response.json()
            print("Response:")
            print(json.dumps(response_data, indent=2))
        except:
            print("Response Text:")
            print(response.text)
    elif response.status_code == 401:
        print("❌ Authentication failed")
        try:
            response_data = response.json()
            print("Error:")
            print(json.dumps(response_data, indent=2))
        except:
            print("Response Text:")
            print(response.text)
    elif response.status_code == 500:
        print("❌ Internal Server Error!")
        try:
            response_data = response.json()
            print("Error:")
            print(json.dumps(response_data, indent=2))
        except:
            print("Response Text:")
            print(response.text)
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print("Response Text:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

