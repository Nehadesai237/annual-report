"""Test registration with actual user data"""
import requests
import json

def test_registration():
    """Test registration with the data from the form"""
    url = "http://localhost:8000/api/v1/auth/register"
    
    data = {
        "name": "Rajnandini dhanaji desai",
        "email": "akashpatil@gmail.com",
        "password": "TestPassword123!@#",
        "confirm_password": "TestPassword123!@#",
        "department": "Computer",
        "role": "student",
        "student_id": "CS2024005",
        "year_of_study": 2,
        "phone": "+91 9356840897"
    }
    
    print("=" * 60)
    print("Testing Registration")
    print("=" * 60)
    print("\nRegistration Data:")
    for key, value in data.items():
        if 'password' in key:
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")
    print()
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print("\n✅ Registration successful!")
            result = response.json()
            print(json.dumps(result, indent=2))
        else:
            print("\n❌ Registration failed")
            print(f"\nResponse:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"\n❌ Request failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_registration()

