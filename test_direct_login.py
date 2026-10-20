"""
Test backend login directly
"""
import requests
import json

url = "http://localhost:8000/api/v1/auth/login"
data = {
    "email": "test@tkiet.edu.in",
    "password": "Test@123",
    "remember_me": False
}

print("Testing direct backend connection...")
try:
    response = requests.post(url, json=data, timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful!")
        result = response.json()
        print(f"Token: {result['access_token'][:50]}...")
    else:
        print(f"Response: {response.text}")
except requests.exceptions.Timeout:
    print("❌ Request timed out!")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

