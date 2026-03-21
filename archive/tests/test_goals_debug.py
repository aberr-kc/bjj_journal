import sqlite3
import requests
import json

# Check database schema
print("=== Checking Database Schema ===")
conn = sqlite3.connect('data/bjj_journal.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(user_goals)")
columns = cursor.fetchall()
print("user_goals table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check existing goals
cursor.execute("SELECT * FROM user_goals WHERE is_active = 1")
goals = cursor.fetchall()
print(f"\nActive goals: {len(goals)}")
for goal in goals:
    print(f"  Goal: {goal}")

conn.close()

# Test API
print("\n=== Testing API ===")
try:
    # Login first
    login_data = {"username": "test", "password": "test"}
    login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current goals
        goals_response = requests.get("http://localhost:8000/goals/current", headers=headers)
        print(f"Current goals status: {goals_response.status_code}")
        if goals_response.status_code == 200:
            print(f"Current goals: {goals_response.json()}")
        else:
            print(f"No current goals: {goals_response.text}")
            
        # Test creating a goal with rounds
        test_goal = {
            "weekly_sessions_target": 3,
            "weekly_rounds_target": 15,
            "start_date": "2024-01-16"
        }
        
        create_response = requests.post("http://localhost:8000/goals/", json=test_goal, headers=headers)
        print(f"Create goal status: {create_response.status_code}")
        print(f"Create goal response: {create_response.text}")
        
    else:
        print(f"Login failed: {login_response.status_code}")
        
except Exception as e:
    print(f"API test error: {e}")