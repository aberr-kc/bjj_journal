import requests
from datetime import datetime, timedelta
import json

class GarminConnectAPI:
    def __init__(self):
        self.base_url = "https://connect.garmin.com"
        self.session = requests.Session()
        self.is_authenticated = False
    
    def login(self, username, password):
        """Login to Garmin Connect with your credentials"""
        # Step 1: Get login form
        login_url = f"{self.base_url}/signin"
        response = self.session.get(login_url)
        
        # Step 2: Submit credentials
        login_data = {
            'username': username,
            'password': password,
            'embed': 'false'
        }
        
        response = self.session.post(
            f"{self.base_url}/signin",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if "dashboard" in response.url:
            self.is_authenticated = True
            print("✅ Successfully logged into Garmin Connect")
            return True
        else:
            print("❌ Login failed")
            return False
    
    def get_activities(self, start_date=None, limit=20):
        """Get recent activities"""
        if not self.is_authenticated:
            print("Not authenticated. Please login first.")
            return []
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/modern/proxy/activitylist-service/activities/search/activities"
        params = {
            'start': 0,
            'limit': limit,
            'startDate': start_str,
            'endDate': end_str
        }
        
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            activities = response.json()
            return activities
        else:
            print(f"Failed to get activities: {response.status_code}")
            return []
    
    def get_bjj_activities(self):
        """Filter for BJJ activities"""
        activities = self.get_activities()
        bjj_activities = []
        
        for activity in activities:
            activity_name = activity.get('activityName', '').lower()
            activity_type = activity.get('activityType', {}).get('typeKey', '').lower()
            
            # Look for BJJ in name or martial arts activity type
            if ('bjj' in activity_name or 
                'jiu jitsu' in activity_name or 
                'martial' in activity_type or
                'combat' in activity_type):
                
                bjj_activities.append({
                    'activity_id': activity.get('activityId'),
                    'activity_name': activity.get('activityName'),
                    'start_time': activity.get('startTimeLocal'),
                    'duration_minutes': activity.get('duration', 0) // 60,
                    'calories': activity.get('calories', 0),
                    'avg_heart_rate': activity.get('averageHR'),
                    'max_heart_rate': activity.get('maxHR')
                })
        
        return bjj_activities

def test_real_garmin_data():
    """Test with your real Garmin Connect data"""
    
    # Initialize Garmin API
    garmin = GarminConnectAPI()
    
    # Login with your Garmin credentials
    username = input("Enter your Garmin Connect username: ")
    password = input("Enter your Garmin Connect password: ")
    
    if not garmin.login(username, password):
        return
    
    # Get BJJ activities
    print("\nFetching BJJ activities...")
    bjj_activities = garmin.get_bjj_activities()
    
    if not bjj_activities:
        print("No BJJ activities found. Try logging a 'BJJ' activity in Garmin Connect first.")
        return
    
    print(f"\nFound {len(bjj_activities)} BJJ activities:")
    for i, activity in enumerate(bjj_activities):
        print(f"{i+1}. {activity['activity_name']} - {activity['start_time']}")
        print(f"   Duration: {activity['duration_minutes']} min, Calories: {activity['calories']}")
        print(f"   HR: {activity['avg_heart_rate']}/{activity['max_heart_rate']} bpm")
    
    # Send to your journal API
    choice = input(f"\nWhich activity to send to journal? (1-{len(bjj_activities)}): ")
    try:
        selected = bjj_activities[int(choice) - 1]
        
        # Send to your journal
        journal_data = {
            "activity_name": selected['activity_name'],
            "duration_minutes": selected['duration_minutes'],
            "calories": selected['calories'],
            "avg_heart_rate": selected['avg_heart_rate'] or 0,
            "max_heart_rate": selected['max_heart_rate'] or 0,
            "timestamp": selected['start_time'],
            "activity_id": str(selected['activity_id'])
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/garmin/activity",
            json=journal_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Activity sent to journal! Entry ID: {result['entry_id']}")
            print("Now complete the journal entry in your web app.")
        else:
            print(f"❌ Failed to send to journal: {response.text}")
            
    except (ValueError, IndexError):
        print("Invalid selection")

if __name__ == "__main__":
    test_real_garmin_data()