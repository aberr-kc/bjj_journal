import requests
from datetime import datetime

def create_manual_bjj_activity():
    """Create a realistic BJJ activity manually"""
    
    print("Creating manual BJJ activity with realistic data...")
    
    # Realistic BJJ training data
    activity_data = {
        "activity_name": "BJJ Training - Evening Class",
        "duration_minutes": 90,  # 1.5 hour class
        "calories": 720,  # High intensity
        "avg_heart_rate": 148,  # Moderate-high intensity
        "max_heart_rate": 182,  # Peak during rolling
        "timestamp": datetime.now().isoformat(),
        "activity_id": f"manual_bjj_{int(datetime.now().timestamp())}"
    }
    
    print(f"Activity Details:")
    print(f"- Name: {activity_data['activity_name']}")
    print(f"- Duration: {activity_data['duration_minutes']} minutes")
    print(f"- Calories: {activity_data['calories']}")
    print(f"- Heart Rate: {activity_data['avg_heart_rate']} avg / {activity_data['max_heart_rate']} max")
    
    # Send to journal
    response = requests.post(
        "http://127.0.0.1:8000/garmin/activity",
        json=activity_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Manual activity created! Entry ID: {result['entry_id']}")
        print("Status:", result['status'])
        print("\nNow go to your journal web app to complete the entry!")
        return result['entry_id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def check_pending_entries():
    """Check what pending entries exist"""
    
    # You'll need to login first to get token
    login_data = {"username": "test", "password": "test123"}  # Use your test user
    login_response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get("http://127.0.0.1:8000/entries/pending", headers=headers)
        
        if response.status_code == 200:
            pending = response.json()
            print(f"\nPending entries: {len(pending)}")
            for entry in pending:
                print(f"- ID {entry['id']}: {entry['duration_minutes']} min, {entry['avg_heart_rate']} bpm")
        else:
            print("Failed to get pending entries")
    else:
        print("Login failed")

if __name__ == "__main__":
    entry_id = create_manual_bjj_activity()
    if entry_id:
        check_pending_entries()