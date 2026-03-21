import requests

# Login
login_response = requests.post("http://localhost:8000/auth/login", json={"username": "test", "password": "test"})
token = login_response.json()["access_token"]

# Test active injuries endpoint
response = requests.get("http://localhost:8000/injuries/active", headers={"Authorization": f"Bearer {token}"})
print(f"Status: {response.status_code}")
print(f"Active injuries: {response.json()}")

# Test all injuries
all_response = requests.get("http://localhost:8000/injuries/", headers={"Authorization": f"Bearer {token}"})
print(f"\nAll injuries:")
for injury in all_response.json():
    print(f"  ID: {injury['id']}, Area: {injury['injured_area']}, End Date: {injury['end_date']}")
