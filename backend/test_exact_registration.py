"""Test registration with EXACT data from user"""
import requests
import json

def test_exact_registration():
    """Test with exact data from user's form"""
    
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
    print("Testing EXACT registration data")
    print("=" * 60)
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/auth/register',
            json=data,
            timeout=10
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 500:
            print("\n*** 500 ERROR RESPONSE ***")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print("Response text:", response.text)
        
        elif response.status_code == 422:
            print("\nValidation Error:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print("Response text:", response.text)
        
        elif response.status_code == 201:
            print("\n✅ SUCCESS!")
            print(json.dumps(response.json(), indent=2))
        
        else:
            print(f"\nUnexpected status: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\nException: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_registration()

