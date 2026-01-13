#!/usr/bin/env python3
import sys
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.database import SQLALCHEMY_DATABASE_URL

def reset_password(username: str, new_password: str):
    # Create database connection
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found")
            return False
        
        # Hash new password using bcrypt directly
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        user.hashed_password = hashed_password
        db.commit()
        
        print(f"Password updated successfully for user '{username}'")
        return True
        
    except Exception as e:
        print(f"Error updating password: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    reset_password("abarr", "test")