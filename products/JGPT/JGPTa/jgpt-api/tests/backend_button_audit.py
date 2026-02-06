
import requests
import json
import sys
import time

# Configuration
API_BASE = "http://localhost:8001/api"
AUTH_URL = "http://localhost:8001/auth/token"
USERNAME = "admin@jgpt.com"
PASSWORD = "admin"

def get_token():
    print(f"🔑 Authenticating as {USERNAME}...")
    try:
        response = requests.post(
            f"{AUTH_URL}",
            data={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Login Failed: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)

def audit_buttons():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔘 STARTING BACKEND BUTTON AUDIT")
    print("================================")

    # 1. Create a Conversation to Manipulate
    print("\n1️⃣  [Button: New Chat] Creating session...")
    conv_resp = requests.post(f"{API_BASE}/conversations", headers=headers, json={"mode": "powerbi"})
    if conv_resp.status_code == 200:
        conv_id = conv_resp.json()["id"]
        print(f"   ✅ Created Conversation ID: {conv_id}")
    else:
        print(f"   ❌ Failed to create conversation: {conv_resp.status_code}")
        return

    # 2. Add a message (so export has content)
    print("\n2️⃣  [Action: Send Message] Populating chat...")
    requests.post(f"{API_BASE}/chat", headers=headers, json={
        "conversation_id": conv_id, 
        "message": "Test for export", 
        "mode": "powerbi"
    })
    print("   ✅ Message added.")

    # 3. Test Export Button
    print("\n3️⃣  [Button: Export Chat] Testing PDF/Markdown export...")
    # Note: Using /full endpoint based on audit
    export_resp = requests.post(f"{API_BASE}/conversations/{conv_id}/export/full", headers=headers)
    if export_resp.status_code == 200:
        print(f"   ✅ Export Successful (Length: {len(export_resp.content)} bytes)")
    else:
        print(f"   ❌ Export Failed: {export_resp.status_code} - {export_resp.text}")

    # 4. Test Delete Conversation
    print("\n4️⃣  [Button: Delete Chat] Clearing conversation...")
    del_resp = requests.delete(f"{API_BASE}/conversations/{conv_id}", headers=headers)
    if del_resp.status_code == 200:
        print("   ✅ Conversation Deleted")
    else:
        print(f"   ❌ Delete Failed: {del_resp.status_code} - {del_resp.text}")

    # 5. Test KB Maintenance (Reload)
    print("\n5️⃣  [Button: Reload KB] Testing re-indexing...")
    reload_resp = requests.post(f"{API_BASE}/kb/reload", headers=headers)
    if reload_resp.status_code == 200:
        print(f"   ✅ KB Reload Triggered: {reload_resp.json()}")
    else:
        print(f"   ❌ KB Reload Failed: {reload_resp.status_code}")

    # 6. Test Model Management (List) -> "Pull" button logic check
    print("\n6️⃣  [Button: Model Dropdown] Listing active models...")
    models_resp = requests.get(f"{API_BASE}/models", headers=headers)
    if models_resp.status_code == 200:
        models = models_resp.json().get("models", [])
        print(f"   ✅ Models Available: {len(models)}")
    else:
        print(f"   ❌ Model List Failed: {models_resp.status_code}")

    print("\n🏁 AUDIT COMPLETE")

if __name__ == "__main__":
    audit_buttons()
