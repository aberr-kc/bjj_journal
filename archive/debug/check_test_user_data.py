from app.database import SessionLocal
from app.models import User, Entry, Response, Question

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == 'test').first()
    if user:
        print(f"User ID: {user.id}")
        entries = db.query(Entry).filter(Entry.user_id == user.id).all()
        print(f"Total entries: {len(entries)}")
        
        for entry in entries:
            print(f"\nEntry ID: {entry.id}, Date: {entry.date}")
            for response in entry.responses:
                print(f"  - {response.question.question_text}: {response.answer}")
    else:
        print("User 'test' not found")
finally:
    db.close()
