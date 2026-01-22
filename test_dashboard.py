import requests

PROD_URL = "https://bjjjournal-production.up.railway.app"

def test_dashboard_endpoint():
    print("=== Testing Dashboard Endpoint ===")
    
    # Login first
    response = requests.post(f"{PROD_URL}/auth/login", 
                           json={"username": "test", "password": "test"})
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test dashboard endpoint
    print("\nTesting /analytics/dashboard endpoint...")
    response = requests.get(f"{PROD_URL}/analytics/dashboard", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Dashboard data received:")
        print(f"  Total sessions: {data.get('total_sessions', 'N/A')}")
        print(f"  Average RPE: {data.get('avg_rpe', 'N/A')}")
        print(f"  Total rounds: {data.get('total_rounds', 'N/A')}")
        print(f"  Session types: {data.get('session_types', {})}")
        
        if data.get('total_sessions', 0) == 0:
            print("\n⚠️  Dashboard shows 0 sessions - this is why it's blank!")
        else:
            print("\n✅ Dashboard has data - frontend issue")
    else:
        print(f"Dashboard endpoint failed: {response.text}")
    
    # Test entries endpoint for comparison
    print("\nTesting /entries/ endpoint...")
    response = requests.get(f"{PROD_URL}/entries/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        entries = response.json()
        print(f"Entries found: {len(entries)}")
        for i, entry in enumerate(entries[:3]):
            print(f"  Entry {i+1}: {entry['date'][:10]} - {len(entry.get('responses', []))} responses")

if __name__ == "__main__":
    test_dashboard_endpoint()