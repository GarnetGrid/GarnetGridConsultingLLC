import requests
import json
import os

API_KEY = os.getenv("JGPT_API_KEY", "jgpt_master_key")
BASE_URL = "http://localhost:8000"

def test_hybrid_retrieval(query):
    print(f"\n--- Testing Query: {query} ---")
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "message": query,
        "history": [],
        "stream": False
    }
    
    resp = requests.post(f"{BASE_URL}/chat", headers=headers, json=payload)
    if resp.status_code != 200:
        print(f"FAILED: {resp.status_code} - {resp.text}")
        return

    data = resp.json()
    citations = data.get("citations", [])
    retrieval = data.get("retrieval", {})
    
    print(f"Retrieval Time: {retrieval.get('ms')}ms")
    print(f"Pool Size: {retrieval.get('pool')}")
    print(f"Hybrid Count: {retrieval.get('hybrid_count')}")
    
    for i, c in enumerate(citations[:3]):
        print(f"[{i+1}] Source: {c['source']} | Rank Type: {c.get('rank_type')}")
        print(f"    Snippet: {c['snippet'][:100]}...")

if __name__ == "__main__":
    # Test specific technical terms
    test_hybrid_retrieval("What is DMF used for?")
    test_hybrid_retrieval("X++ query patterns")
