from app.database import SessionLocal
from app.models import Entry, Response, Question, User
from datetime import datetime, timedelta, timezone

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == 'test').first()
    print(f"User: {user.username} (ID: {user.id})")
    
    # Get recent entries (last 30 days)
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=30)
    entries = db.query(Entry).filter(
        Entry.user_id == user.id,
        Entry.date >= start_date
    ).all()
    print(f"Found {len(entries)} entries in last 30 days")
    
    # Get responses for these entries
    entry_ids = [e.id for e in entries]
    responses = db.query(Response).filter(Response.entry_id.in_(entry_ids)).all()
    print(f"Found {len(responses)} responses for these entries")
    
    # Check questions
    questions = db.query(Question).all()
    print(f"Found {len(questions)} questions")
    for q in questions:
        print(f"  Q{q.id}: {q.question_text}")
    
    # Check response-question relationships
    print("\nChecking response-question relationships:")
    for r in responses[:5]:  # Just first 5
        question = db.query(Question).filter(Question.id == r.question_id).first()
        if question:
            print(f"  Response {r.id}: Q{r.question_id} '{question.question_text}' = '{r.answer}'")
        else:
            print(f"  Response {r.id}: Q{r.question_id} (MISSING QUESTION) = '{r.answer}'")
    
    # Test the specific query from analytics
    print("\nTesting analytics query:")
    responses_with_questions = db.query(Response).filter(Response.entry_id.in_(entry_ids)).all()
    print(f"Raw responses: {len(responses_with_questions)}")
    
    # Check for responses with question relationships
    responses_with_valid_questions = []
    for r in responses_with_questions:
        if r.question:
            responses_with_valid_questions.append(r)
    
    print(f"Responses with valid question relationships: {len(responses_with_valid_questions)}")
    
finally:
    db.close()