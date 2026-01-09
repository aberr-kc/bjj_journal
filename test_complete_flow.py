#!/usr/bin/env python3
"""Simple test to create a BJJ entry with simulated Garmin data"""

import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

def test_complete_flow():
    """Test the complete BJJ Journal flow"""
    
    # Step 1: Register a user
    print("1. Creating test user...")
    user_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code == 200:
        print("✅ User created")
    else:
        print("ℹ️ User might already exist")
    
    # Step 2: Login
    print("2. Logging in...")
    response = requests.post(f"{API_BASE}/auth/login", json=user_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
    else:
        print("❌ Login failed")
        return
    
    # Step 3: Get questions
    print("3. Getting questions...")
    response = requests.get(f"{API_BASE}/questions/")
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ Got {len(questions)} questions")
    else:
        print("❌ Failed to get questions")
        return
    
    # Step 4: Create entry with simulated Garmin data
    print("4. Creating BJJ entry with simulated Garmin data...")
    
    # Prepare responses (simulate filling out the form)
    responses = []
    for q in questions:
        if "Session Type" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "Gi"})
        elif "Rate of Perceived Exertion" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "7"})
        elif "Training" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "High Intensity"})
        elif "Class Technique" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "Guard passing, submissions from side control"})
        elif "Rounds Rolled" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "6"})
        elif "Journal Notes" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "Great session! Worked on pressure passing and finished with several submissions. Felt strong today."})
        elif "Summarise" in q["question_text"]:
            responses.append({"question_id": q["id"], "answer": "Strong technical session with good rolls"})
    
    # Entry data with simulated Garmin metrics
    entry_data = {
        "date": datetime.now().isoformat(),
        "session_type": "training",
        "responses": responses,
        # Simulated Garmin data
        "garmin_activity_id": "12345678901",
        "duration_minutes": 90,
        "calories_burned": 650,
        "avg_heart_rate": 145,
        "max_heart_rate": 178
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/entries/", json=entry_data, headers=headers)
    
    if response.status_code == 200:
        entry = response.json()
        print("✅ Entry created successfully!")
        print(f"   Entry ID: {entry['id']}")
        print(f"   Duration: {entry.get('duration_minutes', 'N/A')} minutes")
        print(f"   Calories: {entry.get('calories_burned', 'N/A')}")
        print(f"   Avg HR: {entry.get('avg_heart_rate', 'N/A')} bpm")
        
        # Step 5: Test dashboard
        print("5. Testing dashboard...")
        response = requests.get(f"{API_BASE}/analytics/dashboard", headers=headers)
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Dashboard data:")
            print(f"   Total sessions: {dashboard['total_sessions']}")
            print(f"   This month: {dashboard['this_month']}")
            print(f"   Average RPE: {dashboard['avg_rpe']}")
            
        print("\\n🎉 Test completed successfully!")
        print("\\nNext steps:")
        print("1. Open frontend.html in your browser")
        print("2. Login with username: testuser, password: password123")
        print("3. Check the dashboard and activities")
        
    else:
        print(f"❌ Failed to create entry: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("🥋 BJJ Journal - Complete Flow Test")
    print("=" * 40)
    test_complete_flow()