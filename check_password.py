#!/usr/bin/env python3
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.database import SQLALCHEMY_DATABASE_URL

def check_user_password(username: str):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            return
        
        print(f"User: {username}")
        print(f"Password hash: {user.hashed_password}")
        
        # Test common passwords
        test_passwords = ["test", "password", "123456", "abarr"]
        for pwd in test_passwords:
            hash_test = hashlib.sha256(pwd.encode()).hexdigest()
            if hash_test == user.hashed_password:
                print(f"Current password is: {pwd}")
                return
        
        print("Password not found in common list")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user_password("abarr")