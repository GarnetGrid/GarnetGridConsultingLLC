
import urllib.request
import urllib.parse
import json
import ssl

# Bypass SSL if needed (though localhost is http)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

API_BASE = "http://localhost:8000"

def get_token():
    try:
        url = f"{API_BASE}/auth/token"
        data = urllib.parse.urlencode({"username": "user@jgpt.com", "password": "jgpt-premium"}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, context=ctx) as response:
            resp_body = response.read()
            return json.loads(resp_body)["access_token"]
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def fetch_models(token):
    try:
        url = f"{API_BASE}/api/models"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, context=ctx) as response:
            resp_body = response.read()
            print(json.loads(resp_body))
    except Exception as e:
        print(f"Fetch failed: {e}")

token = get_token()
if token:
    print("Got token.")
    fetch_models(token)
