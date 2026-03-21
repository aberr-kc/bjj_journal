import requests
from datetime import datetime

def input_real_training_data():
    """Input your actual training data from Garmin Connect"""
    
    print("🥋 Enter your real BJJ training data:")
    print("(Check Garmin Connect for these values)")
    
    activity_name = input("Activity name (e.g., 'BJJ Training'): ") or "BJJ Training"
    duration = int(input("Duration in minutes: ") or "75")
    calories = int(input("Calories burned: ") or "650")
    avg_hr = int(input("Average heart rate: ") or "145")
    max_hr = int(input("Max heart rate: ") or "175")
    
    activity_data = {
        "activity_name": activity_name,
        "duration_minutes": duration,
        "calories": calories,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "timestamp": datetime.now().isoformat(),
        "activity_id": f"real_{int(datetime.now().timestamp())}"
    }
    
    print(f"\n📡 Sending real data to journal...")
    response = requests.post("http://127.0.0.1:8000/garmin/activity", json=activity_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Real training data sent! Entry ID: {result['entry_id']}")
        print("Now complete your journal entry!")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    input_real_training_data()