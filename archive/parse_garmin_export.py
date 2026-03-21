import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import os

def parse_garmin_export():
    """Parse exported TCX/GPX file from Garmin Connect"""
    
    print("🥋 Parse Real Garmin Data")
    print("1. Go to connect.garmin.com")
    print("2. Find your BJJ activity")
    print("3. Click gear icon → Export → TCX")
    print("4. Save the file to this folder")
    print()
    
    # Look for TCX files in current directory
    tcx_files = [f for f in os.listdir('.') if f.endswith('.tcx')]
    
    if not tcx_files:
        print("No TCX files found. Please export from Garmin Connect first.")
        return
    
    print("Found TCX files:")
    for i, file in enumerate(tcx_files, 1):
        print(f"{i}. {file}")
    
    choice = input(f"Select file (1-{len(tcx_files)}): ")
    
    try:
        selected_file = tcx_files[int(choice) - 1]
        
        # Parse TCX file
        tree = ET.parse(selected_file)
        root = tree.getroot()
        
        # Extract activity data
        activity_data = extract_tcx_data(root)
        
        if activity_data:
            print(f"\n📊 Extracted Data:")
            print(f"Duration: {activity_data['duration_minutes']} minutes")
            print(f"Calories: {activity_data['calories']}")
            print(f"Avg HR: {activity_data['avg_heart_rate']} bpm")
            print(f"Max HR: {activity_data['max_heart_rate']} bpm")
            
            # Send to journal
            response = requests.post(
                "http://127.0.0.1:8000/garmin/activity",
                json=activity_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Real Garmin data sent to journal!")
                print(f"Entry ID: {result['entry_id']}")
                print("Now complete your journal entry!")
            else:
                print(f"❌ Failed to send: {response.text}")
        
    except (ValueError, IndexError, FileNotFoundError) as e:
        print(f"Error: {e}")

def extract_tcx_data(root):
    """Extract relevant data from TCX XML"""
    
    # TCX namespace
    ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    activity = root.find('.//tcx:Activity', ns)
    if not activity:
        print("No activity found in TCX file")
        return None
    
    # Get activity name and time
    activity_name = "BJJ Training - Garmin Export"
    start_time = activity.find('tcx:Id', ns)
    
    # Get laps for duration and calories
    laps = activity.findall('.//tcx:Lap', ns)
    total_duration = 0
    total_calories = 0
    heart_rates = []
    
    for lap in laps:
        # Duration in seconds
        duration_elem = lap.find('tcx:TotalTimeSeconds', ns)
        if duration_elem is not None:
            total_duration += float(duration_elem.text)
        
        # Calories
        calories_elem = lap.find('tcx:Calories', ns)
        if calories_elem is not None:
            total_calories += int(calories_elem.text)
        
        # Heart rate data
        avg_hr_elem = lap.find('.//tcx:AverageHeartRateBpm/tcx:Value', ns)
        max_hr_elem = lap.find('.//tcx:MaximumHeartRateBpm/tcx:Value', ns)
        
        if avg_hr_elem is not None:
            heart_rates.append(int(avg_hr_elem.text))
        if max_hr_elem is not None:
            heart_rates.append(int(max_hr_elem.text))
    
    # Calculate averages
    duration_minutes = int(total_duration / 60)
    avg_hr = int(sum(heart_rates) / len(heart_rates)) if heart_rates else 0
    max_hr = max(heart_rates) if heart_rates else 0
    
    return {
        "activity_name": activity_name,
        "duration_minutes": duration_minutes,
        "calories": total_calories,
        "avg_heart_rate": avg_hr,
        "max_heart_rate": max_hr,
        "timestamp": datetime.now().isoformat(),
        "activity_id": f"garmin_export_{int(datetime.now().timestamp())}"
    }

if __name__ == "__main__":
    parse_garmin_export()