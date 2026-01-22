import requests
import json
from datetime import datetime, timedelta
import random

PROD_URL = "https://bjjjournal-production.up.railway.app"

# Training data options
SESSION_TYPES = ["Gi", "No Gi", "Both"]
TRAINING_TYPES = ["Regular Class", "Open Mat", "Competition Training", "Drilling Session"]
TECHNIQUES = [
    "Closed Guard - Armbar",
    "Mount - Cross Collar Choke", 
    "Side Control - Kimura",
    "Back Control - Rear Naked Choke",
    "Half Guard - Sweep"
]

def add_production_data():
    print("=== Adding Test Data to Production ===")
    
    # Login
    response = requests.post(f"{PROD_URL}/auth/login", 
                           json={"username": "test", "password": "test"})
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get questions
    response = requests.get(f"{PROD_URL}/questions/", headers=headers)
    questions = response.json()
    print(f"Found {len(questions)} questions")
    
    if not questions:
        print("No questions found! Check if app started correctly.")
        return
    
    # Create 10 test entries
    print("Creating test entries...")
    success_count = 0
    
    for i in range(10):
        # Generate entry for last 10 days
        date = datetime.now() - timedelta(days=i)
        
        # Generate random data
        session_type = random.choice(SESSION_TYPES)
        training_type = random.choice(TRAINING_TYPES)
        technique = random.choice(TECHNIQUES)
        rpe = random.randint(5, 8)
        rounds = random.randint(4, 8)
        
        # Map responses to questions
        responses = []
        for question in questions:
            if "Session Type" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": session_type})
            elif "Rate of Perceived Exertion" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": str(rpe)})
            elif "Training" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": training_type})
            elif "Class Technique" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": technique})
            elif "Rounds Rolled" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": str(rounds)})
            elif "Journal Notes" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": f"Good session on {date.strftime('%Y-%m-%d')}. Worked on {technique.lower()}."})
            elif "Summarise" in question["question_text"]:
                responses.append({"question_id": question["id"], "answer": f"Day {i+1} - {training_type}"})
        
        entry_data = {
            "date": date.isoformat(),
            "session_type": "training",
            "responses": responses
        }
        
        response = requests.post(f"{PROD_URL}/entries/", headers=headers, json=entry_data)
        if response.status_code == 200:
            success_count += 1
            print(f"  Created entry {i+1}/10")
        else:
            print(f"  Failed entry {i+1}: {response.text}")
    
    print(f"Successfully created {success_count}/10 entries")
    
    # Verify final count
    response = requests.get(f"{PROD_URL}/entries/", headers=headers)
    final_entries = response.json()
    print(f"Final entry count: {len(final_entries)}")

if __name__ == "__main__":
    add_production_data()