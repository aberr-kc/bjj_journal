import sqlite3

conn = sqlite3.connect('data/bjj_journal.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE entries ADD COLUMN injured_during_session BOOLEAN DEFAULT 0')
    conn.commit()
    print('Added injured_during_session column to entries table')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e).lower():
        print('Column already exists')
    else:
        raise
finally:
    conn.close()
