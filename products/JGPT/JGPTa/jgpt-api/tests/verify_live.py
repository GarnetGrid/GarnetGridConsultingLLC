import requests
import json
import sys

API_BASE = "http://localhost:8000"
USERNAME = "admin@jgpt.com"
PASSWORD = "admin"

def run():
    # 1. Login
    print(f"Logging in as {USERNAME}...")
    try:
        resp = requests.post(f"{API_BASE}/auth/token", data={"username": USERNAME, "password": PASSWORD})
        resp.raise_for_status()
        token = resp.json()["access_token"]
        print("✅ Login successful")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ingest URL
    print("\nTesting Ingestion (https://example.com)...")
    try:
        resp = requests.post(f"{API_BASE}/api/ingest/url", params={"url": "https://example.com"}, headers=headers)
        if resp.status_code == 200:
             print(f"✅ Ingestion successful: {resp.json()}")
        else:
             print(f"❌ Ingestion failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ Ingestion error: {e}")

    # 3. Chat
    print("\nTesting Chat...")
    try:
        data = {
            "message": "Summarize the example domain.",
            "model": "llama3.2",
            "options": {"temperature": 0.7}
        }
        # Note: Chat endpoint returns a stream usually, but we can check if it connects.
        # fastAPI StreamingResponse
        resp = requests.post(f"{API_BASE}/api/chat", json=data, headers=headers, stream=True)
        if resp.status_code == 200:
            print("✅ Chat connected successfully. Streaming bytes...")
            # Read a bit of the stream
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    print(f"Received chunk: {chunk[:100]}...")
                    break # Just proof of life
        else:
            print(f"❌ Chat failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ Chat error: {e}")

    # 4. KB Stats
    print("\nTesting KB Stats...")
    try:
        resp = requests.get(f"{API_BASE}/api/kb/stats", headers=headers)
        if resp.status_code == 200:
            print(f"✅ KB Stats: {resp.json()}")
        else:
            print(f"❌ KB Stats failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ KB Stats error: {e}")

    # 5. Conversations List
    print("\nTesting Conversations List...")
    try:
        resp = requests.get(f"{API_BASE}/api/conversations", headers=headers)
        if resp.status_code == 200:
            print(f"✅ Conversations: {len(resp.json())} found")
        else:
            print(f"❌ Conversations list failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"❌ Conversations list error: {e}")

if __name__ == "__main__":
    run()
