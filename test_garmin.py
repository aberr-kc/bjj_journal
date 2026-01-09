import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_garmin_endpoints():
    print("Testing Garmin integration endpoints...")
    
    # Test 1: Send mock Garmin activity
    print("\n1. Testing Garmin activity webhook...")
    activity_data = {
        "activity_name": "BJJ Training",
        "duration_minutes": 75,
        "calories": 650,
        "avg_heart_rate": 145,
        "max_heart_rate": 178,
        "timestamp": datetime.now().isoformat(),
        "activity_id": "test_activity_123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/garmin/activity", json=activity_data)
        print(f"Activity webhook: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Created entry ID: {result.get('entry_id')}")
            print(f"Status: {result.get('status')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test 2: Get widget data (will fail without auth, but tests endpoint exists)
    print("\n2. Testing widget data endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/garmin/widget-data")
        print(f"Widget data: {response.status_code}")
        if response.status_code == 401:
            print("Endpoint exists (401 = needs authentication)")
        elif response.status_code == 200:
            print("Widget data retrieved successfully")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_garmin_endpoints()