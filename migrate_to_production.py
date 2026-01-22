#!/usr/bin/env python3
import sqlite3
import psycopg2
import json
import os
from datetime import datetime

# Local SQLite connection
sqlite_conn = sqlite3.connect('data/bjj_journal.db')
sqlite_conn.row_factory = sqlite3.Row

# Production PostgreSQL connection - replace with your Railway DATABASE_URL
DATABASE_URL = "postgresql://username:password@host:port/database"  # Get this from Railway
pg_conn = psycopg2.connect(DATABASE_URL)
pg_cursor = pg_conn.cursor()

def migrate_data():
    print("Starting data migration...")
    
    # Get local users
    sqlite_cursor = sqlite_conn.execute('SELECT * FROM users')
    users = [dict(row) for row in sqlite_cursor.fetchall()]
    
    for user in users:
        print(f"Migrating user: {user['username']}")
        
        # Insert user into production
        pg_cursor.execute("""
            INSERT INTO users (username, hashed_password, created_at) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (username) DO NOTHING
            RETURNING id
        """, (user['username'], user['hashed_password'], user['created_at']))
        
        result = pg_cursor.fetchone()
        if result:
            prod_user_id = result[0]
        else:
            # User already exists, get their ID
            pg_cursor.execute("SELECT id FROM users WHERE username = %s", (user['username'],))
            prod_user_id = pg_cursor.fetchone()[0]
        
        # Get user's entries
        sqlite_cursor = sqlite_conn.execute('SELECT * FROM entries WHERE user_id = ?', (user['id'],))
        entries = [dict(row) for row in sqlite_cursor.fetchall()]
        
        for entry in entries:
            print(f"  Migrating entry from {entry['date']}")
            
            # Insert entry
            pg_cursor.execute("""
                INSERT INTO entries (user_id, date, session_type, created_at) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
            """, (prod_user_id, entry['date'], entry['session_type'], entry['created_at']))
            
            prod_entry_id = pg_cursor.fetchone()[0]
            
            # Get entry responses
            sqlite_cursor = sqlite_conn.execute('SELECT * FROM responses WHERE entry_id = ?', (entry['id'],))
            responses = [dict(row) for row in sqlite_cursor.fetchall()]
            
            for response in responses:
                pg_cursor.execute("""
                    INSERT INTO responses (entry_id, question_id, answer) 
                    VALUES (%s, %s, %s)
                """, (prod_entry_id, response['question_id'], response['answer']))
    
    pg_conn.commit()
    print("Migration completed!")

if __name__ == "__main__":
    print("Replace DATABASE_URL with your Railway PostgreSQL URL before running!")
    print("Get it from Railway dashboard > PostgreSQL service > Variables tab")
    # migrate_data()  # Uncomment after setting DATABASE_URL