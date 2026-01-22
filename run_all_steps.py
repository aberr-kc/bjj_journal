import requests
import json
from collections import defaultdict

# EDIT THESE VALUES:
PROD_API_BASE = "https://bjjjournal-production.up.railway.app"  # ← CHANGE THIS
USERNAME = "test"  # ← CHANGE IF DIFFERENT
PASSWORD = "test"  # ← CHANGE IF DIFFERENT

def run_all_steps():
    print("=== Running All Production Debug Steps ===")
    
    if "YOUR-RAILWAY-APP" in PROD_API_BASE:
        print("[ERROR] Please edit this script and update PROD_API_BASE with your Railway URL")
        return
    
    try:
        # Step 1: Login
        print("\n1. Logging in...")
        response = requests.post(f"{PROD_API_BASE}/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD
        })
        
        if response.status_code != 200:
            print(f"[ERROR] Login failed: {response.text}")
            return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[OK] Login successful")
        
        # Step 2: Debug current state
        print("\n2. Checking current database state...")
        
        # Get questions
        response = requests.get(f"{PROD_API_BASE}/questions/", headers=headers)
        questions = response.json()
        print(f"   Questions: {len(questions)}")
        
        # Get entries
        response = requests.get(f"{PROD_API_BASE}/entries/", headers=headers)
        entries = response.json()
        print(f"   Total entries: {len(entries)}")
        
        # Check for duplicates
        entries_by_date = defaultdict(list)
        for entry in entries:
            date_key = entry['date'][:10]
            entries_by_date[date_key].append(entry)
        
        duplicate_dates = {date: entries for date, entries in entries_by_date.items() if len(entries) > 1}
        print(f"   Duplicate dates: {len(duplicate_dates)}")
        
        if duplicate_dates:
            print("   Duplicate entries found:")
            for date, date_entries in duplicate_dates.items():
                print(f"     {date}: {len(date_entries)} entries")
        
        # Step 3: Clean duplicates if found
        if duplicate_dates:
            print("\n3. Cleaning duplicate entries...")
            deleted_count = 0
            
            for date, date_entries in duplicate_dates.items():
                # Keep the first, delete the rest
                for entry in date_entries[1:]:
                    print(f"   Deleting duplicate entry {entry['id']} from {date}")
                    delete_response = requests.delete(
                        f"{PROD_API_BASE}/entries/{entry['id']}", 
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        deleted_count += 1
                    else:
                        print(f"     [ERROR] Failed: {delete_response.text}")
            
            print(f"[OK] Deleted {deleted_count} duplicate entries")
        else:
            print("\n3. No duplicates found, skipping cleanup")
        
        # Step 4: Final verification
        print("\n4. Final verification...")
        response = requests.get(f"{PROD_API_BASE}/entries/", headers=headers)
        final_entries = response.json()
        print(f"   Final entry count: {len(final_entries)}")
        
        # Show recent entries
        if final_entries:
            print("   Recent entries:")
            for entry in final_entries[:5]:
                print(f"     {entry['date'][:10]} - {entry['session_type']}")
        
        print("\n[OK] All steps completed!")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_steps()