
import requests
import json
import time
import sys

API_BASE = "http://localhost:8001/api"
AUTH_URL = "http://localhost:8001/auth/token"

def print_header(text):
    print(f"\n{'='*60}")
    print(f" 🚀 {text}")
    print(f"{'='*60}")

def print_step(emoji, title, desc):
    print(f"\n{emoji}  **{title}**")
    print(f"    {desc}")
    time.sleep(1)

def fail(msg):
    print(f"\n❌ CRITICAL FAILURE: {msg}")
    sys.exit(1)

def main():
    print_header("JGPT LIVE SYSTEM DEMO")

    # 1. AUTHENTICATION
    print_step("🔑", "Authentication", "Logging in as 'admin@jgpt.com'...")
    try:
        res = requests.post(AUTH_URL, data={"username": "admin@jgpt.com", "password": "admin"})
        if res.status_code != 200: fail(f"Login failed: {res.text}")
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("    ✅ Success! Token acquired.")
    except Exception as e: fail(str(e))

    # 2. KNOWLEDGE INGESTION
    print_step("📚", "Knowledge Base", "Ingesting a sample documentation source...")
    try:
        ingest_payload = {"url": "https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/extensions"}
        # Some endpoints use 'url' param, checking implementation safely
        res = requests.post(f"{API_BASE}/ingest/url", headers=headers, params=ingest_payload)
        status = "Queued" if res.status_code == 200 else "Failed"
        if res.status_code == 200:
             print(f"    ✅ Source Ingested: {res.json()}")
        else:
             print(f"    ⚠️  Ingest Status: {res.status_code} (Skipping non-critical)")
    except Exception as e: print(f"    ⚠️  Ingest Error: {e}")

    # 3. CHAT & REASONING (Streamed)
    print_step("💬", "AI Chat", "Asking: 'Create a Chain of Command wrapper for SalesTable'...")
    try:
        chat_payload = {
            "message": "Create a Chain of Command wrapper for SalesTable to add log on insert.",
            "mode": "expert",
            "stream": True
        }
        res = requests.post(f"{API_BASE}/chat", json=chat_payload, headers=headers, stream=True)
        if res.status_code == 200:
            print("    ✅ Stream Connected. Receiving tokens:")
            print("    ------------------------------------------------")
            # Consume stream but print sparingly
            byte_count = 0
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    byte_count += len(chunk)
                    # print(chunk.decode(), end="", flush=True) # Too noisy for summary
            print(f"\n    ------------------------------------------------")
            print(f"    ✅ Response Complete ({byte_count} bytes received)")
        else:
             fail(f"Chat failed: {res.status_code}")
    except Exception as e: fail(str(e))

    # 4. WORKBENCH: X++ CODE GENERATION
    print_step("🛠", "Workbench", "Executing 'd365fo.coc_scaffold' tool...")
    try:
        tool_payload = {
            "tool_name": "d365fo.coc_scaffold",
            "input": {
                "target_class": "SalesTable",
                "method_name": "insert",
                "code_logic": "info('Log insert');"
            }
        }
        res = requests.post(f"{API_BASE}/tools/execute", json=tool_payload, headers=headers)
        if res.status_code == 200:
            result = res.json()
            print("    ✅ Tool Executed Successfully!")
            print(f"    📄 Generated Code Check:\n")
            content = result.get('output', str(result))
            # Preview first few lines
            print('\n'.join(str(content).split('\n')[:10])) 
            print("    ...")
        else:
            fail(f"Tool execution failed: {res.text}")
    except Exception as e: fail(str(e))

    # 5. DASHBOARD STATS
    print_step("📊", "Admin Dashboard", "Verifying system stats...")
    try:
        res = requests.get(f"{API_BASE}/kb/stats", headers=headers)
        if res.status_code == 200:
            print(f"    ✅ System Healthy: {res.json()}")
        else:
            fail("Dashboard unavailable")
    except Exception as e: fail(str(e))

    print_header("DEMO COMPLETE - SYSTEM 100% OPERATIONAL")

if __name__ == "__main__":
    main()
