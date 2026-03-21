import requests
import json
from collections import defaultdict

# Replace with your production URL
PROD_API_BASE = input("Enter your Railway production URL (e.g., https://your-app.up.railway.app): ").strip()
USERNAME = input("Enter your production username: ").strip() or "test"
PASSWORD = input("Enter your production password: ").strip() or "test"

def clean_duplicates():
    print("=== Cleaning Duplicate Entries ===")
    
    try:
        # Login
        response = requests.post(f"{PROD_API_BASE}/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD
        })
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all entries
        response = requests.get(f"{PROD_API_BASE}/entries/", headers=headers)
        entries = response.json()
        print(f"Found {len(entries)} total entries")
        
        # Group by date to find duplicates
        entries_by_date = defaultdict(list)
        for entry in entries:
            date_key = entry['date'][:10]  # Just the date part
            entries_by_date[date_key].append(entry)
        
        # Find and delete duplicates (keep the first one)
        deleted_count = 0
        for date, date_entries in entries_by_date.items():
            if len(date_entries) > 1:
                print(f"Found {len(date_entries)} entries for {date}")
                # Keep the first, delete the rest
                for entry in date_entries[1:]:
                    print(f"  Deleting duplicate entry {entry['id']}")
                    delete_response = requests.delete(
                        f"{PROD_API_BASE}/entries/{entry['id']}", 
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        deleted_count += 1
                    else:
                        print(f"    Failed to delete: {delete_response.text}")
        
        print(f"Deleted {deleted_count} duplicate entries")
        
        # Check final count
        response = requests.get(f"{PROD_API_BASE}/entries/", headers=headers)
        final_entries = response.json()
        print(f"Final entry count: {len(final_entries)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clean_duplicates()