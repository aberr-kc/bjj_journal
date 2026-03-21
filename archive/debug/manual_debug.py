import requests
import json

PROD_URL = "https://bjjjournal-production.up.railway.app"

def test_endpoints():
    print("=== Testing Production Endpoints ===")
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    try:
        response = requests.get(PROD_URL, timeout=10)
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   Failed: {e}")
        return
    
    # Test 2: Try to register a user first
    print("\n2. Testing user registration...")
    try:
        response = requests.post(f"{PROD_URL}/auth/register", 
                               json={"username": "test", "password": "test"},
                               timeout=10)
        print(f"   Register status: {response.status_code}")
        if response.status_code not in [200, 400]:  # 400 = user exists
            print(f"   Register response: {response.text}")
    except Exception as e:
        print(f"   Register failed: {e}")
    
    # Test 3: Try to login
    print("\n3. Testing login...")
    try:
        response = requests.post(f"{PROD_URL}/auth/login", 
                               json={"username": "test", "password": "test"},
                               timeout=10)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("   Login successful!")
            
            # Test 4: Get entries
            print("\n4. Testing entries endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{PROD_URL}/entries/", headers=headers, timeout=10)
            print(f"   Entries status: {response.status_code}")
            
            if response.status_code == 200:
                entries = response.json()
                print(f"   Found {len(entries)} entries")
                
                # Show first few entries
                for i, entry in enumerate(entries[:3]):
                    print(f"     Entry {i+1}: {entry['date'][:10]} - {entry.get('session_type', 'unknown')}")
            else:
                print(f"   Entries error: {response.text}")
        else:
            print(f"   Login failed: {response.text}")
            
    except Exception as e:
        print(f"   Login failed: {e}")

if __name__ == "__main__":
    test_endpoints()