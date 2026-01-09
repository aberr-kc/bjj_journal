import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Testing BJJ Journal API...")
    
    # Test 1: Register user
    print("\n1. Testing user registration...")
    register_data = {"username": "testuser", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Register response: {response.status_code} - {response.json()}")
    
    # Test 2: Login user
    print("\n2. Testing user login...")
    response = requests.post(f"{BASE_URL}/auth/login", json=register_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Login successful, token received")
    else:
        print(f"Login failed: {response.status_code} - {response.json()}")
        return
    
    # Test 3: Get questions
    print("\n3. Testing get questions...")
    response = requests.get(f"{BASE_URL}/questions/")
    questions = response.json()
    print(f"Found {len(questions)} questions")
    
    # Test 4: Create entry
    print("\n4. Testing create entry...")
    entry_data = {
        "date": datetime.now().isoformat(),
        "session_type": "gi",
        "responses": [
            {"question_id": 1, "answer": "Gi training"},
            {"question_id": 2, "answer": "90"},
            {"question_id": 3, "answer": "8"},
            {"question_id": 4, "answer": "Guard passes and submissions"},
            {"question_id": 6, "answer": "Good flow in rolling"}
        ]
    }
    response = requests.post(f"{BASE_URL}/entries/", json=entry_data, headers=headers)
    if response.status_code == 200:
        entry = response.json()
        entry_id = entry["id"]
        print(f"Entry created with ID: {entry_id}")
    else:
        print(f"Entry creation failed: {response.status_code} - {response.json()}")
        return
    
    # Test 5: Get entries
    print("\n5. Testing get entries...")
    response = requests.get(f"{BASE_URL}/entries/", headers=headers)
    entries = response.json()
    print(f"Found {len(entries)} entries")
    
    # Test 6: Get specific entry
    print("\n6. Testing get specific entry...")
    response = requests.get(f"{BASE_URL}/entries/{entry_id}", headers=headers)
    entry = response.json()
    print(f"Entry details: {entry['session_type']} on {entry['date'][:10]}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_api()