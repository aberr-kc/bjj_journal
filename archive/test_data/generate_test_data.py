import requests
import json
from datetime import datetime, timedelta
import random

# API configuration
API_BASE = "http://localhost:8000"
USERNAME = "test"
PASSWORD = "test"

# Training data options
SESSION_TYPES = ["Gi", "No Gi", "Both"]
TRAINING_TYPES = ["Regular Class", "Open Mat", "Competition Training", "Drilling Session", "Private Lesson", "Seminar/Workshop", "Light Training"]
POSITIONS = ["Closed Guard", "Open Guard", "Half Guard", "Mount", "Side Control", "Back Control", "Butterfly Guard", "De La Riva Guard", "X-Guard", "Spider Guard"]
SKILLS = ["Attacks/Submissions", "Sweeps", "Escapes", "Defense", "Setups", "Transitions"]
SUBMISSIONS = [
    "Armbar", "Triangle Choke", "Rear Naked Choke", "Kimura", "Omoplata", 
    "Guillotine Choke", "D'Arce Choke", "Heel Hook", "Americana", "Ezekiel Choke",
    "Bow and Arrow Choke", "Cross Collar Choke", "Baseball Choke", "Anaconda Choke",
    "Toe Hold", "Knee Bar", "Calf Slicer", "Bicep Slicer", "Wrist Lock",
    "North South Choke", "Paper Cutter Choke", "Loop Choke", "Peruvian Necktie",
    "Gogoplata", "Buggy Choke", "Von Flue Choke", "Arm Triangle", "Japanese Necktie",
    "Straight Ankle Lock", "Estima Lock", "Twister", "Banana Split", "Oil Check"
]

NOTES_OPTIONS = [
    "Worked on guard retention\nFocused on hip movement\nGood rolling sessions",
    "Struggled with takedowns\nImproved bottom game\nNeed to work on cardio",
    "Great technique session\nLearned new sweep variations\nFeeling more confident",
    "Tough training day\nGot submitted multiple times\nLearning from mistakes",
    "Focused on fundamentals\nDrilled basic positions\nSolid foundation work",
    "Competition prep\nHigh intensity rolling\nWorked on game plan",
    "Recovery session\nLight drilling only\nFocused on technique",
    "New techniques learned\nPracticed with different partners\nGood variety today"
]

SUMMARIES = [
    "Great session", "Tough training", "Technical focus", "Competition prep", 
    "Recovery day", "Fundamentals", "New techniques", "Solid work",
    "Challenging rolls", "Good progress", "Technique heavy", "Cardio focused"
]

def login():
    """Login and get access token"""
    response = requests.post(f"{API_BASE}/auth/register", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    response = requests.post(f"{API_BASE}/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def get_questions(token):
    """Get all questions"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/questions/", headers=headers)
    return response.json()

def create_training_entry(token, questions, date):
    """Create a single training entry"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Generate random training data
    session_type = random.choice(SESSION_TYPES)
    training_type = random.choice(TRAINING_TYPES)
    rpe = random.randint(4, 9)  # More realistic RPE range
    rounds = random.randint(3, 12)
    
    # Generate technique
    position = random.choice(POSITIONS)
    skill = random.choice(SKILLS)
    if skill == "Attacks/Submissions":
        technique = f"{position} - {random.choice(SUBMISSIONS)}"
    else:
        technique = f"{position} - {skill}"
    
    notes = random.choice(NOTES_OPTIONS)
    summary = random.choice(SUMMARIES)
    
    # Map responses to questions
    responses = []
    for question in questions:
        if question["question_text"] == "Session Type":
            responses.append({"question_id": question["id"], "answer": session_type})
        elif question["question_text"] == "Rate of Perceived Exertion (1-9)":
            responses.append({"question_id": question["id"], "answer": str(rpe)})
        elif question["question_text"] == "Training":
            responses.append({"question_id": question["id"], "answer": training_type})
        elif question["question_text"] == "Class Technique":
            responses.append({"question_id": question["id"], "answer": technique})
        elif question["question_text"] == "Rounds Rolled":
            responses.append({"question_id": question["id"], "answer": str(rounds)})
        elif question["question_text"] == "Journal Notes":
            responses.append({"question_id": question["id"], "answer": notes})
        elif question["question_text"] == "Summarise this session with a few words":
            responses.append({"question_id": question["id"], "answer": summary})
    
    entry_data = {
        "date": date.isoformat(),
        "session_type": "training",
        "responses": responses
    }
    
    response = requests.post(f"{API_BASE}/entries/", headers=headers, json=entry_data)
    return response.status_code == 200

def generate_training_dates():
    """Generate training dates for 12 months, 4 times per week"""
    dates = []
    start_date = datetime.now() - timedelta(days=365)
    current_date = start_date
    
    while current_date <= datetime.now():
        # Train Monday, Tuesday, Thursday, Saturday (4 times per week)
        if current_date.weekday() in [0, 1, 3, 5]:  # Mon, Tue, Thu, Sat
            # 85% chance of training (to simulate missed sessions)
            if random.random() < 0.85:
                dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates

def main():
    print("Generating BJJ training data...")
    
    try:
        # Login
        print("Logging in...")
        token = login()
        print("Login successful")
        
        # Get questions
        print("Getting questions...")
        questions = get_questions(token)
        print(f"Found {len(questions)} questions")
        
        # Generate training dates
        print("Generating training schedule...")
        training_dates = generate_training_dates()
        print(f"Generated {len(training_dates)} training sessions")
        
        # Create entries
        print("Creating training entries...")
        success_count = 0
        for i, date in enumerate(training_dates):
            if create_training_entry(token, questions, date):
                success_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"  Created {i + 1}/{len(training_dates)} entries...")
        
        print(f"Successfully created {success_count}/{len(training_dates)} training entries")
        print("Data generation complete!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()