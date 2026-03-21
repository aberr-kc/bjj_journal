from app.database import SessionLocal
from app.models import Entry, Response, Question, User
from datetime import datetime, timedelta, timezone

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == 'test').first()
    print(f"User: {user.username} (ID: {user.id})")
    
    # Replicate exact analytics logic
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=30)
    
    entries = db.query(Entry).filter(
        Entry.user_id == user.id,
        Entry.date >= start_date
    ).all()
    print(f"Found {len(entries)} entries")
    
    # This is the exact query from analytics
    entry_ids = [e.id for e in entries]
    print(f"Entry IDs: {entry_ids[:5]}...")  # Show first 5
    
    responses = db.query(Response).filter(Response.entry_id.in_(entry_ids)).all()
    print(f"Found {len(responses)} responses using .in_() query")
    
    # Try alternative query
    if entry_ids:
        responses2 = db.query(Response).filter(Response.entry_id == entry_ids[0]).all()
        print(f"Found {len(responses2)} responses for first entry ID {entry_ids[0]}")
    
    # Check if the issue is with the relationship loading
    for r in responses[:3]:
        print(f"Response {r.id}: entry_id={r.entry_id}, question_id={r.question_id}")
        print(f"  Question object: {r.question}")
        if r.question:
            print(f"  Question text: '{r.question.question_text}'")
    
finally:
    db.close()