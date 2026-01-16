#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime
import os

def backup_database():
    """Export all data to JSON backup file"""
    conn = sqlite3.connect('data/bjj_journal.db')
    conn.row_factory = sqlite3.Row
    
    backup_data = {
        'backup_date': datetime.now().isoformat(),
        'users': [],
        'entries': [],
        'responses': []
    }
    
    # Export users
    cursor = conn.execute('SELECT * FROM users')
    backup_data['users'] = [dict(row) for row in cursor.fetchall()]
    
    # Export entries
    cursor = conn.execute('SELECT * FROM entries')
    backup_data['entries'] = [dict(row) for row in cursor.fetchall()]
    
    # Export responses
    cursor = conn.execute('SELECT * FROM responses')
    backup_data['responses'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Save backup
    os.makedirs('backups', exist_ok=True)
    filename = f"backups/bjj_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"Backup saved to {filename}")
    return filename

if __name__ == "__main__":
    backup_database()