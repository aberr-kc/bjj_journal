import requests
from datetime import datetime

def remove_dummy_data():
    """Remove dummy data from user abarr, keeping only entries from 09/01/2026"""
    
    # Login as abarr
    login_data = {"username": "abarr", "password": "Tuibarr2024!"}
    login_response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("[ERROR] Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all entries
    response = requests.get("http://127.0.0.1:8000/entries/", headers=headers)
    
    if response.status_code != 200:
        print("[ERROR] Failed to get entries")
        return
    
    entries = response.json()
    print(f"Found {len(entries)} total entries")
    
    # Filter entries to delete (not from 09/01/2026)
    keep_date = "2026-01-09"  # ISO format
    entries_to_delete = []
    entries_to_keep = []
    
    for entry in entries:
        entry_date = entry.get('timestamp', '')[:10]  # Get YYYY-MM-DD part
        if entry_date == keep_date:
            entries_to_keep.append(entry)
        else:
            entries_to_delete.append(entry)
    
    print(f"Keeping {len(entries_to_keep)} entries from 09/01/2026")
    print(f"Deleting {len(entries_to_delete)} dummy entries")
    
    # Delete dummy entries
    deleted_count = 0
    for entry in entries_to_delete:
        delete_response = requests.delete(f"http://127.0.0.1:8000/entries/{entry['id']}", headers=headers)
        if delete_response.status_code == 200:
            deleted_count += 1
            entry_date = entry.get('timestamp', '')[:10]
            print(f"[OK] Deleted entry {entry['id']} from {entry_date}: {entry.get('activity_name', 'Unknown')}")
        else:
            print(f"[ERROR] Failed to delete entry {entry['id']}")
    
    print(f"\n[SUCCESS] Removed {deleted_count} dummy entries from user abarr")
    print(f"[SUCCESS] Kept {len(entries_to_keep)} entries from 09/01/2026")

if __name__ == "__main__":
    remove_dummy_data()