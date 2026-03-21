from app.database import SessionLocal, engine
from sqlalchemy import text

db = SessionLocal()
try:
    # Check if column exists
    result = db.execute(text("PRAGMA table_info(injury_logs)"))
    columns = [row[1] for row in result]
    
    if 'end_date' not in columns:
        print("Adding end_date column...")
        db.execute(text("ALTER TABLE injury_logs ADD COLUMN end_date DATE"))
        db.commit()
        print("Column added successfully!")
    else:
        print("end_date column already exists")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
