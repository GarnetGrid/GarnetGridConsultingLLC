import urllib.request
import urllib.error
import json
import sys

def check_url(url, name, expected_status=200, method="GET"):
    print(f"Checking {name} ({url})...", end=" ")
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            if status == expected_status:
                print(f"✅ PASSED ({status})")
                return True
            else:
                print(f"❌ FAILED (Expected {expected_status}, got {status})")
                return False
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
             print(f"✅ PASSED ({e.code} - Expected)")
             return True
        else:
            print(f"❌ FAILED (Expected {expected_status}, got {e.code})")
            return False
    except urllib.error.URLError as e:
        print(f"❌ FAILED (Connection Refused/Error: {e.reason})")
        return False
    except Exception as e:
        print(f"❌ FAILED (Error: {e})")
        return False

def main():
    print("=== JGPT System Audit ===")
    
    # 1. Frontend
    frontend_ok = check_url("http://localhost:3000", "Frontend UI")
    
    # 2. Backend Health
    backend_ok = check_url("http://localhost:8000/api/health", "Backend Health")
    
    # 3. Reasoner Route (Protected)
    # Expect 401 because we treat no-token as unauthorized, verifying route exists
    # Wait, 401 is standard for FastAPI Depends(get_current_user)
    reasoner_ok = check_url("http://localhost:8000/api/reason/chat", "Reasoner Endpoint (Auth Check)", expected_status=401, method="POST")

    print("-" * 30)
    if frontend_ok and backend_ok and reasoner_ok:
        print("🚀 SYSTEM STATUS: LIVE & HEALTHY")
        sys.exit(0)
    else:
        print("⚠️ SYSTEM STATUS: ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()
