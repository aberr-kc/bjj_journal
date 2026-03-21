#!/usr/bin/env python3
import requests
import json
from datetime import date, timedelta

API_BASE = "http://localhost:8000"

def test_goals_api():
    print("Testing Goals API...")
    
    # Test user credentials
    username = "test"
    password = "test123"
    
    # Login to get token
    print("\n1. Logging in...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "username": username,
        "password": password
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        print("Please ensure the test user exists with correct password")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Test 1: Create a goal
    print("\n2. Creating a weekly goal...")
    goal_data = {
        "weekly_sessions_target": 4,
        "start_date": str(date.today())
    }
    
    goal_response = requests.post(f"{API_BASE}/goals/", json=goal_data, headers=headers)
    if goal_response.status_code == 200:
        goal = goal_response.json()
        print(f"✓ Goal created: {goal['weekly_sessions_target']} sessions per week")
        print(f"  Goal ID: {goal['id']}")
    else:
        print(f"✗ Goal creation failed: {goal_response.text}")
        return
    
    # Test 2: Get current goal
    print("\n3. Getting current goal...")
    current_goal_response = requests.get(f"{API_BASE}/goals/current", headers=headers)
    if current_goal_response.status_code == 200:
        current_goal = current_goal_response.json()
        if current_goal:
            print(f"✓ Current goal: {current_goal['weekly_sessions_target']} sessions per week")
        else:
            print("✓ No current goal found")
    else:
        print(f"✗ Failed to get current goal: {current_goal_response.text}")
    
    # Test 3: Get current week progress
    print("\n4. Getting current week progress...")
    progress_response = requests.get(f"{API_BASE}/goals/progress/current-week", headers=headers)
    if progress_response.status_code == 200:
        progress = progress_response.json()
        if progress:
            print(f"✓ Current week progress: {progress['sessions_completed']}/{goal_data['weekly_sessions_target']} sessions")
            print(f"  Goal met: {progress['goal_met']}")
            print(f"  Is paused: {progress['is_paused']}")
        else:
            print("✓ No progress data for current week")
    else:
        print(f"✗ Failed to get current week progress: {progress_response.text}")
    
    # Test 4: Get streak information
    print("\n5. Getting streak information...")
    streak_response = requests.get(f"{API_BASE}/goals/streaks/current", headers=headers)
    if streak_response.status_code == 200:
        streak_info = streak_response.json()
        print(f"✓ Current streak: {streak_info['current_streak']} weeks")
        print(f"  Longest streak: {streak_info['longest_streak']} weeks")
        print(f"  This week: {streak_info['current_week_progress']}/{streak_info['current_week_goal']} sessions")
        print(f"  Sessions needed: {streak_info['weeks_until_goal']}")
    else:
        print(f"✗ Failed to get streak info: {streak_response.text}")
    
    # Test 5: Pause current week
    print("\n6. Testing week pause functionality...")
    pause_data = {
        "week_start_date": str(date.today()),
        "is_paused": True
    }
    
    pause_response = requests.post(f"{API_BASE}/goals/progress/pause-week", json=pause_data, headers=headers)
    if pause_response.status_code == 200:
        print("✓ Week paused successfully")
        
        # Check updated progress
        progress_response = requests.get(f"{API_BASE}/goals/progress/current-week", headers=headers)
        if progress_response.status_code == 200:
            progress = progress_response.json()
            if progress:
                print(f"  Updated progress - Is paused: {progress['is_paused']}")
                print(f"  Goal met (with pause): {progress['goal_met']}")
    else:
        print(f"✗ Failed to pause week: {pause_response.text}")
    
    # Test 6: Unpause week
    print("\n7. Testing week unpause...")
    unpause_data = {
        "week_start_date": str(date.today()),
        "is_paused": False
    }
    
    unpause_response = requests.post(f"{API_BASE}/goals/progress/pause-week", json=unpause_data, headers=headers)
    if unpause_response.status_code == 200:
        print("✓ Week unpaused successfully")
    else:
        print(f"✗ Failed to unpause week: {unpause_response.text}")
    
    # Test 7: Get goal history
    print("\n8. Getting goal history...")
    history_response = requests.get(f"{API_BASE}/goals/history", headers=headers)
    if history_response.status_code == 200:
        history = history_response.json()
        print(f"✓ Found {len(history)} goals in history")
        for i, goal in enumerate(history):
            print(f"  Goal {i+1}: {goal['weekly_sessions_target']} sessions/week, Active: {goal['is_active']}")
    else:
        print(f"✗ Failed to get goal history: {history_response.text}")
    
    # Test 8: Get longest streaks
    print("\n9. Getting longest streaks...")
    longest_streaks_response = requests.get(f"{API_BASE}/goals/streaks/longest", headers=headers)
    if longest_streaks_response.status_code == 200:
        streaks = longest_streaks_response.json()
        print(f"✓ Found {len(streaks)} streak records")
        for streak in streaks:
            print(f"  Streak: {streak['streak_length']} weeks, Current: {streak['is_current']}")
    else:
        print(f"✗ Failed to get longest streaks: {longest_streaks_response.text}")
    
    # Test 9: Create some training entries to test progress calculation
    print("\n10. Creating test training entries...")
    today = date.today()
    
    for i in range(2):  # Create 2 entries this week
        entry_date = today - timedelta(days=i)
        entry_data = {
            "date": f"{entry_date}T12:00:00",
            "session_type": "training",
            "responses": [
                {"question_id": 1, "answer": "Gi"},
                {"question_id": 2, "answer": "6"}
            ]
        }
        
        entry_response = requests.post(f"{API_BASE}/entries/", json=entry_data, headers=headers)
        if entry_response.status_code == 200:
            print(f"  ✓ Created training entry for {entry_date}")
        else:
            print(f"  ✗ Failed to create entry for {entry_date}: {entry_response.text}")
    
    # Test 10: Check updated progress after entries
    print("\n11. Checking updated progress after training entries...")
    final_progress_response = requests.get(f"{API_BASE}/goals/progress/current-week", headers=headers)
    if final_progress_response.status_code == 200:
        final_progress = final_progress_response.json()
        if final_progress:
            print(f"✓ Final progress: {final_progress['sessions_completed']}/{goal_data['weekly_sessions_target']} sessions")
            print(f"  Goal met: {final_progress['goal_met']}")
            print(f"  Streak count: {final_progress['streak_count']}")
    
    # Test 11: Final streak check
    print("\n12. Final streak information...")
    final_streak_response = requests.get(f"{API_BASE}/goals/streaks/current", headers=headers)
    if final_streak_response.status_code == 200:
        final_streak = final_streak_response.json()
        print(f"✓ Final current streak: {final_streak['current_streak']} weeks")
        print(f"  Sessions this week: {final_streak['current_week_progress']}/{final_streak['current_week_goal']}")
        print(f"  Sessions still needed: {final_streak['weeks_until_goal']}")
    
    print("\n" + "="*50)
    print("Goals API testing completed!")
    print("="*50)

if __name__ == "__main__":
    test_goals_api()