import requests
import json
import sys
import time

API_BASE = "http://localhost:8001/api"
USERNAME = "admin@jgpt.com"
PASSWORD = "admin"

def get_token():
    print(f"🔑 Authenticating as {USERNAME}...")
    try:
        response = requests.post(
            "http://localhost:8001/auth/token",
            data={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

def test_chat(token, message):
    print(f"\n💬 Testing Chat with: '{message}'")
    try:
        # Fixed payload: backend expects 'message' (str), not 'messages' (list)
        payload = {
            "message": message,
            "mode": "powerbi",
            "stream": False
        }
        
        with requests.post(
            f"{API_BASE}/chat",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            stream=True
        ) as r:
            if r.status_code == 200:
                print("✅ Chat request accepted")
                # Consume a bit
                for chunk in r.iter_lines():
                    if chunk:
                        print("   (Received stream data)")
                        break 
                return True
            else:
                print(f"❌ Chat failed: {r.status_code} {r.text}")
                return False
    except Exception as e:
        print(f"❌ Chat exception: {e}")
        return False

def ingest_dummy_url(token):
    print("\n📚 Testing Ingestion (URL)...")
    # Switched to URL ingestion as file upload endpoint is not exposed
    target_url = "https://example.com"
    
    try:
        r = requests.post(
            f"{API_BASE}/ingest/url",
            json={"url": target_url},
            headers={"Authorization": f"Bearer {token}"},
            params={"url": target_url} # Some endpoints might take query param, but let's check ingest.py: it takes query param 'url'
        )
        # ingest.py: @router.post("/url") async def ingest_single_url(url: str, ...)
        # It takes 'url' as QUERY PARAMETER by default in FastAPI if not specified as Body.
        # Let's try passing as query param.
        
        r = requests.post(
            f"{API_BASE}/ingest/url",
            headers={"Authorization": f"Bearer {token}"},
            params={"url": target_url}
        )
        
        if r.status_code == 200:
            print(f"✅ Ingestion success: {r.json()}")
            return True
        else:
            print(f"❌ Ingestion failed: {r.status_code} {r.text}")
            return False
    except Exception as e:
        print(f"❌ Ingestion exception: {e}")
        return False

def prime_workbench_model(token):
    print("\n🛠 Testing Workbench: Prime Model...")
    tool_id = "powerbi.model_primer"
    # Fixed Schema: columns must be objects with 'name' property
    input_payload = {
        "model_name": "Dummy Sales Model",
        "bim_content": json.dumps({
            "model": {
                "tables": [
                    {
                        "name": "Sales", 
                        "columns": [{"name": "Amount"}, {"name": "Date"}],
                        "measures": [{"name": "Total Sales"}]
                    },
                    {
                        "name": "Customer", 
                        "columns": [{"name": "ID"}, {"name": "Name"}],
                        "measures": []
                    }
                ]
            }
        })
    }
    
    try:
        r = requests.post(
            f"{API_BASE}/tools/execute",
            json={"tool_name": tool_id, "input": input_payload},
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            print(f"✅ Workbench Prime User Memory success: {r.json()}")
            return True
        else:
            print(f"❌ Workbench Prime failed: {r.status_code} {r.text}")
            return False
    except Exception as e:
        print(f"❌ Workbench exception: {e}")
        return False

def run_eval_suite_test(token):
    print("\n⚖️  Testing Eval Suite...")
    try:
        # Check if 'demo_suite' exists, otherwise use 'default' or similar
        # Since we don't know if a suite exists, we'll try a generic trigger.
        # If 500 occurs, it might be due to missing suite configuration.
        r = requests.post(
            f"{API_BASE}/eval", 
            json={"suite": "demo_suite"},
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            print(f"✅ Eval Suite trigger success: {r.json()}")
            return True
        elif r.status_code == 404:
             print("   (Retrying with /evals...)")
             r = requests.post(
                 f"{API_BASE}/evals",
                 json={"suite": "demo_suite"},
                 headers={"Authorization": f"Bearer {token}"}
             )
             if r.status_code == 200:
                 print(f"✅ Eval Suite trigger success: {r.json()}")
                 return True
             
        print(f"❌ Eval Suite failed: {r.status_code} {r.text}")
        return False
    except Exception as e:
        print(f"❌ Eval exception: {e}")
        return False

def main():
    token = get_token()
    
    # 1. Test Chat
    test_chat(token, "Hello, can you hear me?")
    
    # 2. Ingest
    ingest_dummy_url(token)
    
    # 3. Prime Workbench
    prime_workbench_model(token)
    
    # 4. Run Eval
    run_eval_suite_test(token)

if __name__ == "__main__":
    main()
