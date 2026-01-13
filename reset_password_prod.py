#!/usr/bin/env python3
import os
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User

def get_database_url():
    # Check for production database URL first
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Railway PostgreSQL URL might need adjustment
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Fall back to local SQLite
    return "sqlite:///./data/bjj_journal.db"

def reset_password_prod(username: str, new_password: str):
    database_url = get_database_url()
    print(f"Using database: {database_url[:20]}...")
    
    # Create database connection
    engine = create_engine(database_url)
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
    reset_password_prod("abarr", "test")