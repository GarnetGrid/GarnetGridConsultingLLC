import requests

BASE_URL = "http://localhost:8000"

def get_token():
    try:
        resp = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "admin@jgpt.com",
            "password": "admin"
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
        print(f"Auth failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Auth failed with exception: {e}")
    return None

def list_models(token):
    try:
        # Try /api/models based on previous logs showing "GET /api/models"
        resp = requests.get(f"{BASE_URL}/api/models", headers={
            "Authorization": f"Bearer {token}"
        })
        if resp.status_code == 200:
            print("Models Response:")
            import json
            print(json.dumps(resp.json(), indent=2))
        else:
            print(f"List models failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"List models failed with exception: {e}")

token = get_token()
if token:
    list_models(token)
