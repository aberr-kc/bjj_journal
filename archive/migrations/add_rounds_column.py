import sqlite3
import os

# Path to the database
db_path = os.path.join('data', 'bjj_journal.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add the weekly_rounds_target column to user_goals table
    cursor.execute('ALTER TABLE user_goals ADD COLUMN weekly_rounds_target INTEGER')
    conn.commit()
    print("Successfully added weekly_rounds_target column to user_goals table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column weekly_rounds_target already exists")
    else:
        print(f"Error: {e}")
finally:
    conn.close()