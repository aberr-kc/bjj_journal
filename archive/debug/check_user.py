import requests
import json

PROD_URL = "https://bjjjournal-production.up.railway.app"

def check_user_status():
    print("=== Checking User Status in Production ===")
    
    # Test 1: Try to login with existing user
    print("\n1. Testing login with 'test' user...")
    try:
        response = requests.post(f"{PROD_URL}/auth/login", 
                               json={"username": "test", "password": "test"})
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ User 'test' exists and login works")
            token = response.json()["access_token"]
            
            # Check entries for this user
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{PROD_URL}/entries/", headers=headers)
            entries = response.json()
            print(f"   User has {len(entries)} entries")
            return True
            
        elif response.status_code == 401:
            print("   ❌ User 'test' doesn't exist or wrong password")
            
        else:
            print(f"   ❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # Test 2: Try to register the user
    print("\n2. Attempting to register 'test' user...")
    try:
        response = requests.post(f"{PROD_URL}/auth/register", 
                               json={"username": "test", "password": "test"})
        print(f"   Register status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ User 'test' created successfully")
            return True
        elif response.status_code == 400:
            print("   ℹ️  User 'test' already exists")
            return True
        else:
            print(f"   ❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    return False

if __name__ == "__main__":
    check_user_status()