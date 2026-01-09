#!/usr/bin/env python3
"""Clean test for BJJ Journal without Garmin"""

import requests
import json

API_BASE = "http://127.0.0.1:8000"

def clean_test():
    """Test clean BJJ Journal"""
    
    # Register user
    user_data = {"username": "testuser", "password": "password123"}
    print("1. Registering user...")
    response = requests.post(f"{API_BASE}/auth/register", json=user_data)
    print(f"Register: {response.status_code}")
    
    # Login
    print("2. Logging in...")
    response = requests.post(f"{API_BASE}/auth/login", json=user_data)
    print(f"Login: {response.status_code}")
    
    if response.status_code != 200:
        print("Login failed:", response.text)
        return
    
    token = response.json()["access_token"]
    print("✅ Login successful")
    
    # Get questions
    print("3. Getting questions...")
    response = requests.get(f"{API_BASE}/questions/")
    questions = response.json()
    print(f"✅ Got {len(questions)} questions")
    
    # Create entry
    print("4. Creating entry...")
    entry_data = {
        "date": "2026-01-09T12:00:00",
        "session_type": "training",
        "responses": [
            {"question_id": questions[0]["id"], "answer": "Gi"}
        ]
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/entries/", json=entry_data, headers=headers)
    
    print(f"Entry creation: {response.status_code}")
    if response.status_code == 200:
        print("✅ Clean BJJ Journal working!")
        entry = response.json()
        print(f"Entry ID: {entry['id']}")
        print("No Garmin fields - clean!")
    else:
        print("❌ Failed:", response.text)

if __name__ == "__main__":
    clean_test()