"""Capture 500 error from actual email"""
import requests
import json
import time

def test_with_real_email():
    # This is the email from the user's screenshot
    email = "rajnandinidesai381@gmail.com"
    
    print("=" * 60)
    print("Testing with ACTUAL email from user")
    print("=" * 60)
    
    # Try a few different scenarios
    passwords = [
        "password",
        "Password123",
        "Test123!@#",
        "qwerty123"
    ]
    
    for password in passwords:
        print(f"\n{'='*60}")
        print(f"Password: {password}")
        print(f"{'='*60}")
        
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
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 500:
                print("\n*** GOT 500 ERROR ***")
                print("\nResponse:")
                print(response.text)
            
            elif response.status_code == 401:
                print("\nResponse:")
                data = response.json()
                print(json.dumps(data, indent=2))
            
            # Don't try more passwords if we got 500
            if response.status_code == 500:
                break
                
        except Exception as e:
            print(f"\nException: {str(e)}")
        finally:
            time.sleep(0.5)  # Small delay between requests

if __name__ == "__main__":
    test_with_real_email()

