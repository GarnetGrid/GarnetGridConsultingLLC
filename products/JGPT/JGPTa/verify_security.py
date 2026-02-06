from fastapi.testclient import TestClient
import os
import sys

# Add app to path
sys.path.append(os.path.join(os.getcwd(), "jgpt-api"))

# Set test environment
os.environ["JGPT_API_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app

client = TestClient(app)

def test_auth_protection():
    print("--- Testing Security Hardening ---")
    
    # 1. Test health (should be open)
    r = client.get("/health")
    print(f"Health check (open): {r.status_code}")
    assert r.status_code == 200
    
    # 2. Test chat without key (should fail)
    r = client.post("/chat", json={"message": "hi"})
    print(f"Chat without key (restricted): {r.status_code}")
    assert r.status_code == 401
    
    # 3. Test chat with WRONG key (should fail)
    r = client.post("/chat", json={"message": "hi"}, headers={"X-API-Key": "wrong"})
    print(f"Chat with wrong key (restricted): {r.status_code}")
    assert r.status_code == 401
    
    # 4. Test chat with CORRECT key (should pass to next stage - retrieval error if DB not ready)
    # But for auth check, we just want to see if it gets past 401
    r = client.post("/chat", json={"message": "hi"}, headers={"X-API-Key": "test-secret-key"})
    print(f"Chat with correct key: {r.status_code}")
    # It might be 500 or 422 if DB/models fail in memory, but NOT 401
    assert r.status_code != 401

if __name__ == "__main__":
    try:
        test_auth_protection()
        print("✅ Security Verification Passed!")
    except Exception as e:
        print(f"❌ Security Verification Failed: {e}")
        sys.exit(1)
