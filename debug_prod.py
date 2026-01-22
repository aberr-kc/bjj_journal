import requests
import json

# Replace with your production URL
PROD_API_BASE = input("Enter your Railway production URL (e.g., https://your-app.up.railway.app): ").strip()
USERNAME = input("Enter your production username: ").strip() or "test"
PASSWORD = input("Enter your production password: ").strip() or "test"

def debug_production():
    print("=== Production Database Debug ===")
    
    try:
        # Login
        print("1. Logging in...")
        response = requests.post(f"{PROD_API_BASE}/auth/login", json={
            "username": USERNAME,
            "password": PASSWORD
        })
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get questions
        print("2. Checking questions...")
        response = requests.get(f"{PROD_API_BASE}/questions/", headers=headers)
        questions = response.json()
        print(f"   Found {len(questions)} questions")
        
        # Get entries
        print("3. Checking entries...")
        response = requests.get(f"{PROD_API_BASE}/entries/", headers=headers)
        entries = response.json()
        print(f"   Found {len(entries)} entries")
        
        # Show entry details
        for i, entry in enumerate(entries[:5]):  # Show first 5
            print(f"   Entry {i+1}: {entry['date']} - {entry['session_type']}")
            print(f"     Responses: {len(entry.get('responses', []))}")
        
        # Check if entries have same dates (duplicates)
        dates = [entry['date'] for entry in entries]
        unique_dates = set(dates)
        print(f"   Unique dates: {len(unique_dates)}")
        print(f"   Total entries: {len(entries)}")
        
        if len(unique_dates) < len(entries):
            print("   ⚠️  DUPLICATE ENTRIES DETECTED!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_production()