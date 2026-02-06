import requests
import json
import sys

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

def test_tool(token, tool_id, tool_name, input_payload):
    print(f"\n🛠  Testing {tool_name} ({tool_id})...")
    
    # Construct payload explicitly matching frontend logic
    # In frontend runTool(): 
    # body: JSON.stringify({ tool_name: selectedTool, input: toolInput })
    
    payload = {
        "tool_name": tool_id,
        "input": input_payload
    }

    try:
        response = requests.post(
            f"{API_BASE}/tools/execute",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            print(f"✅ Success")
            # print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...") # Truncated
            return True
        else:
            print(f"❌ Failed ({response.status_code})")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    token = get_token()
    print("✅ Auth Token Acquired")

    # Tool definitions and mock inputs based on WorkbenchPanel.tsx PRESETS and logic
    tests = [
        {
            "id": "powerbi.pbi_tools",
            "name": "Power BI Pro Tools",
            "input": {
                "bim_content": '{"model": {"tables": [{"name": "Sales", "columns": [], "measures": []}]}}',
                "action": "parse_schema"
            }
        },
        {
            "id": "powerbi.star_schema_validator",
            "name": "Star Schema Validator",
            "input": {
                "dax": '{"model": {"relationships": [{"fromTable": "Sales", "toTable": "Product", "crossFilteringBehavior": "bothDirections"}]}}', # Using 'dax' field as generic input based on else block logic, though logic specific to validator might expect 'model' content. The frontend assumes 'dax'/'code' for default.
                # Actually, looking at frontend:
                # } else { toolInput = { ...toolInput, dax: input, code: input }; }
                # So we verify generic input handling.
                "code": '{"model": {"relationships": [{"fromTable": "Sales", "toTable": "Product", "crossFilteringBehavior": "bothDirections"}]}}'
            }
        },
        {
            "id": "d365fo.set_based_wizard",
            "name": "Set-Based Wizard",
            "input": {
                "code": 'while select forupdate custTable\n{\n    custTable.CreditMax = 5000;\n    custTable.update();\n}'
            }
        },
        {
            "id": "d365fo.coc_scaffold",
            "name": "CoC Scaffolder",
            "input": {
                "code": "// Method: insert on CustTable"
            }
        },
        {
            "id": "d365fo.d365_metadata",
            "name": "D365FO Metadata",
            "input": {
                "table_name": "CustTable",
                "action": "metadata_lookup"
            }
        },
         {
            "id": "d365fo.project_primer",
            "name": "D365FO Project Primer",
            "input": {
                 "project_name": "MyExtension", 
                 "objects": ["CustTable.Extension", "SalesLine.Extension"], 
                 "description": "Core sales extensions"
            }
        }
    ]

    results = []
    for t in tests:
        success = test_tool(token, t["id"], t["name"], t["input"])
        results.append(success)

    print("\n" + "="*30)
    if all(results):
        print("🚀 ALL TOOLS PASSED")
        sys.exit(0)
    else:
        print("⚠️ SOME TOOLS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
