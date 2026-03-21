from app.database import SessionLocal
from app.models import Entry, Response, Question, User

db = SessionLocal()
try:
    # Get test user
    user = db.query(User).filter(User.username == 'test').first()
    if not user:
        print("No test user found")
        exit()
    
    print(f"User: {user.username} (ID: {user.id})")
    
    # Get entries
    entries = db.query(Entry).filter(Entry.user_id == user.id).all()
    print(f"Found {len(entries)} entries")
    
    # Get responses
    responses = db.query(Response).join(Entry).filter(Entry.user_id == user.id).all()
    print(f"Found {len(responses)} responses")
    
    # Get questions
    questions = db.query(Question).all()
    print(f"Found {len(questions)} questions")
    
    if entries and not responses:
        print("\nProblem: Entries exist but no responses!")
        print("Sample entry:")
        entry = entries[0]
        print(f"  ID: {entry.id}, Date: {entry.date}, Type: {entry.session_type}")
        
        # Check if responses table exists but is empty
        all_responses = db.query(Response).all()
        print(f"Total responses in database: {len(all_responses)}")
        
finally:
    db.close()