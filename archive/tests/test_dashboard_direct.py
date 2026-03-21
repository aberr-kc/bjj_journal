import requests

# Login first
login_data = {"username": "test", "password": "test"}
response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data)
if response.status_code != 200:
    print(f"Login failed: {response.status_code} - {response.json()}")
    exit()

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test dashboard
response = requests.get("http://127.0.0.1:8000/analytics/dashboard", headers=headers)
if response.status_code == 200:
    data = response.json()
    print(f"Total sessions: {data['total_sessions']}")
    print(f"Session types: {data['session_types']}")
    print(f"Total rounds: {data['total_rounds']}")
    print(f"Avg RPE: {data['avg_rpe']}")
else:
    print(f"Dashboard failed: {response.status_code} - {response.json()}")