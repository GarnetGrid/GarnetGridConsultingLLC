
import requests
import json
import sys

API_BASE = "http://localhost:8001/api"
AUTH_URL = "http://localhost:8001/auth/token"

def main():
    print("\n🕵️‍♀️  JGPT DATA WAREHOUSE CONSULTANT DEMO\n")
    
    # 1. Login
    print("1. [Authenticating]...")
    try:
        res = requests.post(AUTH_URL, data={"username": "admin@jgpt.com", "password": "admin"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    # 2. Load Bad Model
    print("2. [Loading Model] Reading 'bad_model.json' (Contains Anti-Patterns)...")
    with open("tests/bad_model.json", "r") as f:
        bim_content = f.read()

    # 3. Request Audit via Workbench
    print("3. [Analyzing] Submitting model to 'Star Schema Validator' tool...")
    payload = {
        "tool_name": "powerbi.star_schema_validator",
        "input": {"bim_content": bim_content}
    }
    
    res = requests.post(f"{API_BASE}/tools/execute", json=payload, headers=headers)
    
    if res.status_code == 200:
        result = res.json()
        print("\n✅ REPORT GENERATED:")
        print("==================================================")
        
        # The tool returns 'output' or 'result' key depending on wrapper
        # Let's inspect what we got
        data = result.get("output", result.get("result", result))
        
        # Pretty print the issues
        if isinstance(data, dict):
            issues = data.get("issues", [])
            print(f"🚨 Issues Found: {len(issues)}\n")
            for issue in issues:
                print(f"  - {issue}")
            
            print(f"\n💡 Recommendation: {data.get('recommendation')}")
        else:
            print(data)
            
        print("==================================================")
    else:
        print(f"❌ Analysis failed: {res.text}")

if __name__ == "__main__":
    main()
