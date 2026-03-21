#!/usr/bin/env python3
"""Minimal test to isolate the issue"""

import requests
import json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

def minimal_test():
    """Minimal test with just required fields"""
    
    # Register user first
    user_data = {"username": "testuser", "password": "password123"}
    requests.post(f"{API_BASE}/auth/register", json=user_data)
    
    # Login
    response = requests.post(f"{API_BASE}/auth/login", json=user_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    
    # Get questions
    response = requests.get(f"{API_BASE}/questions/")
    questions = response.json()
    
    # Create minimal entry (no optional Garmin fields)
    entry_data = {
        "date": "2026-01-09T12:00:00",
        "session_type": "training",
        "responses": [
            {"question_id": questions[0]["id"], "answer": "Gi"}
        ]
    }
    
    print("Sending minimal entry data:")
    print(json.dumps(entry_data, indent=2))
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/entries/", json=entry_data, headers=headers)
    
    print(f"Response: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
    else:
        print("✅ Success!")
        print(response.json())

if __name__ == "__main__":
    minimal_test()