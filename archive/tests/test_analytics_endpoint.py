import requests

# Login
login_response = requests.post("http://localhost:8000/auth/login", json={"username": "test", "password": "test"})
token = login_response.json()["access_token"]

# Test analytics
response = requests.get("http://localhost:8000/analytics/dashboard?period=all", headers={"Authorization": f"Bearer {token}"})
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
