import os, pytest, requests, time, json

pytestmark = pytest.mark.skipif(os.getenv("RUN_INTEGRATION") != "1", reason="Set RUN_INTEGRATION=1 to run integration tests")

API = os.getenv("API_BASE_URL","http://localhost:8000")

def wait_ok(url, tries=30):
    for _ in range(tries):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False

def test_health():
    assert wait_ok(f"{API}/health")

def test_chat_rag():
    payload = {"mode":"powerbi","message":"Why does a measure look right in a card but wrong in a matrix?"}
    r = requests.post(f"{API}/chat", json=payload, timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "citations" in data
