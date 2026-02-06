
import requests
import sys

# Constants
API_BASE = "http://localhost:8001/api"
AUTH_URL = "http://localhost:8001/auth/token"
USERNAME = "admin@jgpt.com"
PASSWORD = "admin"

def get_token():
    try:
        res = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
        if res.status_code == 200:
            return res.json()["access_token"]
        sys.exit(f"❌ Login Failed: {res.status_code}")
    except Exception as e:
        sys.exit(f"❌ Connection Failed: {e}")

def check_page(name, endpoints, token):
    print(f"\n📄 Checking Page: [{name}]")
    headers = {"Authorization": f"Bearer {token}"}
    all_ok = True
    
    for url in endpoints:
        full_url = f"{API_BASE}{url}"
        try:
            r = requests.get(full_url, headers=headers)
            if r.status_code == 200:
                print(f"   ✅ {url} (200 OK)")
            else:
                print(f"   ❌ {url} ({r.status_code})")
                all_ok = False
        except Exception as e:
            print(f"   ❌ {url} (Error: {e})")
            all_ok = False
            
    return all_ok

def run_crawl():
    print("🕷️  STARTING FULL SITE CRAWL")
    print("============================")
    
    token = get_token()
    
    # 1. Dashboard / Chat (Default View)
    # Loads conversations list
    check_page("Home / Chat", ["/conversations"], token)
    
    # 2. Knowledge Tab
    # Loads sources and stats
    check_page("Home / Knowledge", ["/kb/sources", "/kb/stats"], token)
    
    # 3. Workbench Tab
    # Likely loads tools list
    check_page("Home / Workbench", ["/tools/list"], token)
    
    # 4. Evals Tab
    # Loads latest report
    # Note: Might return 404 if no report exists, which is valid logic but a "fail" for the endpoint check
    # We'll allow 404 here if the service is up.
    print(f"\n📄 Checking Page: [Home / Evals]")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/eval/latest", headers=headers)
    if r.status_code in [200, 404]: 
        print(f"   ✅ /eval/latest ({r.status_code} - Expected)")
    else:
        print(f"   ❌ /eval/latest ({r.status_code})")

    # 5. Admin Page
    # Also loads stats
    check_page("Admin Console", ["/kb/stats", "/admin/settings"], token)

    print("\n🏁 CRAWL COMPLETE")

if __name__ == "__main__":
    run_crawl()
