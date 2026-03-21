from app.database import SessionLocal
from app.models import User, Entry, Response

db = SessionLocal()
try:
    # Find test user
    test_user = db.query(User).filter(User.username == 'test').first()
    if test_user:
        # Delete all entries and responses for test user
        db.query(Response).filter(Response.entry_id.in_(
            db.query(Entry.id).filter(Entry.user_id == test_user.id)
        )).delete(synchronize_session=False)
        
        db.query(Entry).filter(Entry.user_id == test_user.id).delete()
        db.commit()
        print(f'Cleared all entries for user: test')
    else:
        print('Test user not found')
finally:
    db.close()
