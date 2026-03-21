import requests

PROD_URL = "https://bjjjournal-production.up.railway.app"

print("Testing connection to production...")
try:
    response = requests.get(PROD_URL, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response length: {len(response.text)}")
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed: {e}")
    print("Your Railway app might be sleeping or having issues.")