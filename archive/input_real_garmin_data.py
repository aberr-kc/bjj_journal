import requests
from datetime import datetime

def input_real_garmin_data():
    """Input your actual Garmin data manually"""
    
    print("🥋 Enter Real BJJ Training Data from Garmin")
    print("(Check your Garmin Connect app or watch for these values)")
    print("=" * 50)
    
    # Get real data from user
    print("\n📱 From your Garmin Connect app or watch:")
    activity_name = input("Activity name (or press Enter for 'BJJ Training'): ").strip()
    if not activity_name:
        activity_name = "BJJ Training"
    
    print("\n⏱️ Duration:")
    duration_str = input("Duration in minutes (e.g., 75): ").strip()
    duration = int(duration_str) if duration_str.isdigit() else 75
    
    print("\n🔥 Calories:")
    calories_str = input("Calories burned (e.g., 650): ").strip()
    calories = int(calories_str) if calories_str.isdigit() else 650
    
    print("\n❤️ Heart Rate:")
    avg_hr_str = input("Average heart rate (e.g., 145): ").strip()
    avg_hr = int(avg_hr_str) if avg_hr_str.isdigit() else 145
    
    max_hr_str = input("Max heart rate (e.g., 175): ").strip()
    max_hr = int(max_hr_str) if max_hr_str.isdigit() else 175
    
    print("\n📅 Date/Time:")
    date_input = input("Date (YYYY-MM-DD) or press Enter for today: ").strip()
    if date_input:
        try:
            date_obj = datetime.strptime(date_input, "%Y-%m-%d")
        except:
            date_obj = datetime.now()
    else:
        date_obj = datetime.now()
    
    # Create activity data
    activity_data = {
        "activity_name": activity_name,
        "duration_minutes": duration,
        "calories": calories,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "timestamp": date_obj.isoformat(),
        "activity_id": f"manual_real_{int(datetime.now().timestamp())}"
    }
    
    # Show summary
    print("\n" + "=" * 50)
    print("📊 REAL GARMIN DATA SUMMARY:")
    print("=" * 50)
    print(f"Activity: {activity_data['activity_name']}")
    print(f"Duration: {activity_data['duration_minutes']} minutes")
    print(f"Calories: {activity_data['calories']}")
    print(f"Heart Rate: {activity_data['avg_heart_rate']} avg / {activity_data['max_heart_rate']} max bpm")
    print(f"Date: {date_obj.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    confirm = input("\nSend this real data to your journal? (y/n): ").lower()
    
    if confirm == 'y':
        print("\n📡 Sending real Garmin data to journal...")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/garmin/activity",
                json=activity_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ SUCCESS! Real Garmin data sent to journal!")
                print(f"Entry ID: {result['entry_id']}")
                print(f"Status: {result['status']}")
                print(f"\n🌐 Now open: http://localhost:3000/frontend.html")
                print("Complete your journal entry with the BJJ-specific questions!")
                
                return result['entry_id']
            else:
                print(f"❌ Failed to send: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Make sure your journal server is running:")
            print("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("Cancelled.")
    
    return None

if __name__ == "__main__":
    input_real_garmin_data()