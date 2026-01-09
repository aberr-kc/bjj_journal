import requests
import json
from datetime import datetime, timedelta
import random

# API configuration
API_BASE = "http://localhost:8000"
USERNAME = "abarr"
PASSWORD = "Tuibarr2024!"

# Sample data for realistic entries
session_types = ["Gi", "No Gi", "Both"]
training_types = ["Skill development", "Rest session", "Drilling", "High Intensity", "Competition Rounds", "Social"]
rpe_ratings = [3, 4, 5, 6, 7, 8, 9]
techniques = [
    "Guard passes and sweeps",
    "Armbar from guard",
    "Triangle choke setups",
    "Back control transitions",
    "Kimura from side control",
    "Butterfly guard sweeps",
    "Leg drag passes",
    "Collar chokes from mount",
    "Escape from side control",
    "Half guard recovery"
]
journal_notes = [
    "Worked on timing for guard passes\nFelt good energy today\nNeed to work on grip fighting",
    "Great drilling session\nImproved triangle setup\nPartner gave good feedback",
    "High intensity rolling\nCardio felt better than last week\nWorked with advanced students",
    "Focused on fundamentals\nSlow controlled movements\nGood technical session",
    "Competition prep training\nPracticed under pressure\nTiming needs work",
    "Social rolling session\nHelped newer students\nRelaxed atmosphere",
    "Back to basics drilling\nWorked on posture\nGood muscle memory building",
    "Intense sparring rounds\nTested new techniques\nGood learning experience",
    "Recovery focused session\nLight drilling only\nWorked on flexibility",
    "Mixed training session\nBoth gi and no-gi\nGood variety today"
]
summaries = [
    "Great technical session",
    "High intensity training",
    "Good drilling day",
    "Solid fundamentals work",
    "Competition prep",
    "Social rolling",
    "Back to basics",
    "Intense sparring",
    "Recovery session",
    "Mixed training"
]

def login():
    """Login and get access token"""
    response = requests.post(f"{API_BASE}/auth/login", 
                           json={"username": USERNAME, "password": PASSWORD})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        return None

def get_questions(token):
    """Get all questions"""
    response = requests.get(f"{API_BASE}/questions/", 
                          headers={"Authorization": f"Bearer {token}"})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get questions: {response.status_code}")
        return []

def create_entry(token, date, responses):
    """Create a training entry"""
    entry_data = {
        "date": date,
        "session_type": "training",
        "responses": responses
    }
    
    response = requests.post(f"{API_BASE}/entries/", 
                           json=entry_data,
                           headers={
                               "Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"
                           })
    
    if response.status_code == 200:
        print(f"Created entry for {date}")
        return True
    else:
        print(f"Failed to create entry for {date}: {response.status_code}")
        return False

def main():
    # Try to login first
    token = login()
    if not token:
        # If login fails, try to register
        print("Login failed, trying to register user...")
        response = requests.post(f"{API_BASE}/auth/register", 
                               json={"username": USERNAME, "password": PASSWORD})
        if response.status_code == 200:
            print(f"User {USERNAME} registered successfully")
            token = login()
        else:
            print(f"Registration also failed: {response.status_code} - {response.text}")
            return
    
    if not token:
        print("Could not get access token")
        return
    
    # Get questions
    questions = get_questions(token)
    if not questions:
        return
    
    # Create question mapping
    question_map = {q["question_text"]: q["id"] for q in questions}
    
    # Generate 10 entries over the last 3 weeks
    base_date = datetime.now() - timedelta(days=21)
    
    for i in range(10):
        # Generate random date within the last 3 weeks
        days_offset = random.randint(0, 20)
        entry_date = base_date + timedelta(days=days_offset)
        date_str = entry_date.strftime("%Y-%m-%dT12:00:00")
        
        # Generate responses
        responses = []
        
        # Session Type
        if "Session Type" in question_map:
            responses.append({
                "question_id": question_map["Session Type"],
                "answer": random.choice(session_types)
            })
        
        # RPE Rating
        if "Rate of Perceived Exertion (1-9)" in question_map:
            responses.append({
                "question_id": question_map["Rate of Perceived Exertion (1-9)"],
                "answer": str(random.choice(rpe_ratings))
            })
        
        # Training Type
        if "Training" in question_map:
            responses.append({
                "question_id": question_map["Training"],
                "answer": random.choice(training_types)
            })
        
        # Class Technique
        if "Class Technique" in question_map:
            responses.append({
                "question_id": question_map["Class Technique"],
                "answer": random.choice(techniques)
            })
        
        # Rounds Rolled
        if "Rounds Rolled" in question_map:
            responses.append({
                "question_id": question_map["Rounds Rolled"],
                "answer": str(random.randint(3, 8))
            })
        
        # Journal Notes
        if "Journal Notes" in question_map:
            responses.append({
                "question_id": question_map["Journal Notes"],
                "answer": random.choice(journal_notes)
            })
        
        # Summary
        if "Summarise this session with a few words" in question_map:
            responses.append({
                "question_id": question_map["Summarise this session with a few words"],
                "answer": random.choice(summaries)
            })
        
        # Create the entry
        create_entry(token, date_str, responses)
    
    print("Finished creating dummy entries!")

if __name__ == "__main__":
    main()