import requests
import json
import sys

API_BASE = "http://localhost:8001/api"
USERNAME = "admin@jgpt.com"
PASSWORD = "admin"

def get_token():
    try:
        response = requests.post(f"http://localhost:8001/auth/token", data={"username": USERNAME, "password": PASSWORD})
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        sys.exit(1)

def run_build_tool(token, name, tool_id, input_data):
    print(f"\n🏗️  Testing Build: {name}...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"tool_name": tool_id, "input": input_data}
    
    try:
        response = requests.post(f"{API_BASE}/tools/execute", json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Build Successful")
            print("--- GENERATED X++ CODE ---")
            # Handle potential variation in output structure
            output = result.get('result', result)
            if isinstance(output, dict):
                print(output.get('code', json.dumps(output, indent=2)))
            else:
                print(output)
            print("--------------------------")
            return True
        else:
            print(f"❌ Build Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    token = get_token()
    
    # Test 1: Set-Based Update (Build logic from slow while loop)
    run_build_tool(token, "Set-Based Wizard", "d365fo.set_based_wizard", {
        "code": "while select forupdate custTable { custTable.CreditMax = 5000; custTable.update(); }"
    })

    # Test 2: Chain of Command Scaffold (Build wrapper)
    run_build_tool(token, "CoC Scaffolder", "d365fo.coc_scaffold", {
        "code": "class: CustTable, method: insert"
    })

if __name__ == "__main__":
    main()
