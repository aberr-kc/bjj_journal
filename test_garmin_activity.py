#!/usr/bin/env python3
"""Test script to simulate Garmin activity data"""

import requests
import json
from datetime import datetime, timedelta

# Your BJJ Journal API
API_BASE = "http://127.0.0.1:8000"

def simulate_garmin_activity():
    """Simulate a Garmin activity being sent to your journal"""
    
    # Sample activity data (matching the API schema)
    activity_data = {
        "activity_name": "BJJ Training Session",
        "duration_minutes": 90,  # 1.5 hour BJJ session
        "calories": 650,
        "avg_heart_rate": 145,
        "max_heart_rate": 178,
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "activity_id": "12345678901"
    }
    
    print("Simulating Garmin activity data:")
    print(json.dumps(activity_data, indent=2))
    
    # Send to your journal's Garmin endpoint
    try:
        response = requests.post(
            f"{API_BASE}/garmin/activity",
            json=activity_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Activity created successfully!")
            print(f"Entry ID: {result.get('entry_id')}")
            print(f"Status: {result.get('status')}")
            return result.get('entry_id')
        else:
            print(f"❌ Failed to create activity: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to BJJ Journal API")
        print("Make sure the server is running on http://127.0.0.1:8000")
        return None

def get_widget_data(entry_id):
    """Get data that would be sent back to Garmin widget"""
    try:
        response = requests.get(f"{API_BASE}/garmin/widget-data")
        
        if response.status_code == 200:
            widget_data = response.json()
            print(f"\n📱 Widget data (what your watch would receive):")
            print(json.dumps(widget_data, indent=2))
        else:
            print(f"❌ Failed to get widget data: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to BJJ Journal API")

if __name__ == "__main__":
    print("🥋 BJJ Journal - Garmin Activity Test")
    print("=" * 40)
    
    entry_id = simulate_garmin_activity()
    
    if entry_id:
        get_widget_data(entry_id)
        
        print(f"\n📝 Next steps:")
        print(f"1. Open frontend.html in your browser")
        print(f"2. Login to your account")
        print(f"3. Check the dashboard for the new activity")
        print(f"4. Complete the journal entry with your training notes")