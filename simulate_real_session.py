import requests
from datetime import datetime
import time

def simulate_real_bjj_session():
    """Simulate a real BJJ training session with realistic data"""
    
    print("🥋 Simulating real BJJ training session...")
    
    # Realistic BJJ session data based on typical training
    sessions = [
        {
            "name": "BJJ - Gi Fundamentals Class",
            "duration": 90,
            "calories": 720,
            "avg_hr": 142,
            "max_hr": 175,
            "description": "Evening fundamentals class with drilling and rolling"
        },
        {
            "name": "BJJ - No-Gi Open Mat",
            "duration": 75,
            "calories": 680,
            "avg_hr": 155,
            "max_hr": 185,
            "description": "High intensity open mat session"
        },
        {
            "name": "BJJ - Competition Training",
            "duration": 120,
            "calories": 950,
            "avg_hr": 160,
            "max_hr": 190,
            "description": "Competition prep with hard rolling"
        }
    ]
    
    print("Available BJJ sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"{i}. {session['name']} ({session['duration']} min)")
        print(f"   Calories: {session['calories']}, HR: {session['avg_hr']}/{session['max_hr']}")
    
    choice = input(f"\nSelect session (1-{len(sessions)}): ")
    
    try:
        selected = sessions[int(choice) - 1]
        
        # Create activity data
        activity_data = {
            "activity_name": selected["name"],
            "duration_minutes": selected["duration"],
            "calories": selected["calories"],
            "avg_heart_rate": selected["avg_hr"],
            "max_heart_rate": selected["max_hr"],
            "timestamp": datetime.now().isoformat(),
            "activity_id": f"sim_{int(time.time())}"
        }
        
        print(f"\n📡 Sending {selected['name']} to journal...")
        print(f"Duration: {selected['duration']} min")
        print(f"Calories: {selected['calories']}")
        print(f"Heart Rate: {selected['avg_hr']}/{selected['max_hr']} bpm")
        
        # Send to your journal
        response = requests.post(
            "http://127.0.0.1:8000/garmin/activity",
            json=activity_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Activity sent successfully!")
            print(f"Entry ID: {result['entry_id']}")
            print(f"Status: {result['status']}")
            print(f"\n🌐 Now open your journal at: http://localhost:3000/frontend.html")
            print("Complete the journal entry with your training details!")
            
            return result['entry_id']
        else:
            print(f"❌ Failed to send: {response.text}")
            
    except (ValueError, IndexError):
        print("Invalid selection")
        return None

def check_widget_data():
    """Test what the watch widget would see"""
    
    # Login to get token
    login_data = {"username": "test", "password": "test123"}
    login_response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n📱 Testing widget data (what your watch would see)...")
        response = requests.get("http://127.0.0.1:8000/garmin/widget-data", headers=headers)
        
        if response.status_code == 200:
            widget_data = response.json()
            print("\n⌚ Watch Widget Display:")
            print("=" * 30)
            
            if widget_data.get("last_session"):
                session = widget_data["last_session"]
                print(f"Last: {session.get('date', 'N/A')} RPE {session.get('rpe', 'N/A')}/9")
                print(f"Type: {session.get('session_type', 'N/A')} {session.get('training_type', '')}")
                print(f"Rounds: {session.get('rounds', '0')} rounds")
            else:
                print("No completed sessions")
            
            print("-" * 30)
            print(f"Week: {widget_data.get('weekly_sessions', 0)} sessions")
            print(f"Streak: {widget_data.get('current_streak', 0)} days")
            print(f"Pending: {widget_data.get('pending_count', 0)} entries")
            print("=" * 30)
        else:
            print(f"Failed to get widget data: {response.text}")
    else:
        print("Login failed - create test user first")

if __name__ == "__main__":
    entry_id = simulate_real_bjj_session()
    if entry_id:
        input("\nPress Enter after completing the journal entry to see widget data...")
        check_widget_data()