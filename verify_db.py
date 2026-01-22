import os
from app.database import engine, SQLALCHEMY_DATABASE_URL

def verify_database():
    print("=== Database Configuration Verification ===")
    
    # Check environment variable
    db_url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL env var: {db_url}")
    
    # Check what database is being used
    print(f"Active database URL: {SQLALCHEMY_DATABASE_URL}")
    
    # Check database type
    if "postgresql" in SQLALCHEMY_DATABASE_URL:
        print("[OK] Using PostgreSQL")
    elif "sqlite" in SQLALCHEMY_DATABASE_URL:
        print("[OK] Using SQLite")
    else:
        print("[?] Unknown database type")
    
    # Test connection
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1")).fetchone()
            print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")

if __name__ == "__main__":
    verify_database()