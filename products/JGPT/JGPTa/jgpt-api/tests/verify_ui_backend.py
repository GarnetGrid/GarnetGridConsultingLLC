import urllib.request
import urllib.parse
import json
import sys

API_BASE = "http://localhost:8000"
import urllib.request
import urllib.parse
import json
import base64
import hashlib
import hmac
import time

API_BASE = "http://localhost:8000"
SECRET_KEY = "jgpt_super_secret_key_change_me_in_prod"

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).replace(b"=", b"").decode("utf-8")

def generate_jwt():
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": "admin@jgpt.com",
        "exp": int(time.time()) + 3600
    }
    
    encoded_header = base64url_encode(json.dumps(header).encode("utf-8"))
    encoded_payload = base64url_encode(json.dumps(payload).encode("utf-8"))
    
    msg = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256
    ).digest()
    encoded_signature = base64url_encode(signature)
    
    return f"{msg}.{encoded_signature}"

HEADERS = {
    "Authorization": f"Bearer {generate_jwt()}",
    "Content-Type": "application/json"
}

def make_request(method, endpoint, data=None):
    url = f"{API_BASE}{endpoint}"
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
    else:
        data_bytes = None
        
    req = urllib.request.Request(url, data=data_bytes, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            if content:
                return resp.status, json.loads(content)
            return resp.status, {}
    except urllib.error.HTTPError as e:
        content = e.read().decode('utf-8')
        try:
            return e.code, json.loads(content)
        except:
            return e.code, content
    except Exception as e:
        print(f"Request Error: {e}")
        return 500, str(e)

def test_connection_lifecycle():
    print(f"Testing Connection Lifecycle against {API_BASE}...")

    # 1. Create a Test Connection
    payload = {
        "name": "VerifyUI_TestDB",
        "type": "postgres",
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "user",
        "password": "password"
    }
    
    print("1. Creating connection... ", end="")
    status, data = make_request("POST", "/api/connections/", payload)
    
    conn_id = None
    if status == 200:
        conn_id = data["id"]
        print(f"SUCCESS (ID: {conn_id})")
    else:
        print(f"FAILED ({status}): {data}")
        return

    # 2. List Connections
    print("2. Listing connections... ", end="")
    status, conns = make_request("GET", "/api/connections/")
    if status == 200:
        found = any(c['id'] == conn_id for c in conns)
        if found:
            print(f"SUCCESS (Found ID {conn_id})")
        else:
            print("FAILED (Created ID not found in list)")
    else:
        print(f"FAILED ({status}): {conns}")

    # 3. Test Connection (Expected Failure as it's fake)
    print("3. Testing connection (expecting failure)... ", end="")
    status, res = make_request("POST", f"/api/connections/{conn_id}/test")
    if status == 400: # Expected failure
         print("SUCCESS (Correctly failed valid connection test)")
    elif status == 200:
         print("WARNING (Unexpected success?)")
    else:
         print(f"FAILED (Unexpected status {status})")

    # 4. Delete Connection
    print("4. Deleting connection... ", end="")
    status, res = make_request("DELETE", f"/api/connections/{conn_id}")
    if status == 200:
        print("SUCCESS")
    else:
         print(f"FAILED ({status}): {res}")
        
    # 5. Verify Deletion
    print("5. Verifying deletion... ", end="")
    status, conns = make_request("GET", "/api/connections/")
    
    if isinstance(conns, list):
        found = any(c['id'] == conn_id for c in conns)
        if not found:
            print("SUCCESS (ID gone)")
        else:
            print("FAILED (ID still present)")
    else:
        print(f"FAILED (Expected list, got {type(conns)}: {conns})")

if __name__ == "__main__":
    test_connection_lifecycle()
