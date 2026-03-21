import sqlite3

conn = sqlite3.connect('data/bjj_journal.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM user_goals WHERE is_active = 1 ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()
print('Latest active goal:', result)

# Get column names
cursor.execute("PRAGMA table_info(user_goals)")
columns = [col[1] for col in cursor.fetchall()]
print('Columns:', columns)

if result:
    goal_dict = dict(zip(columns, result))
    print('Goal as dict:', goal_dict)

conn.close()