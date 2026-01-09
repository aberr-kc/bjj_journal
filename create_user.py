from app.database import SessionLocal
from app.models import User
from app.dependencies import get_password_hash

db = SessionLocal()
try:
    # Check if user exists
    existing_user = db.query(User).filter(User.username == 'test').first()
    if existing_user:
        print('User test already exists')
    else:
        # Create user
        user = User(username='test', hashed_password=get_password_hash('test123'))
        db.add(user)
        db.commit()
        print('User created: test/test123')
finally:
    db.close()