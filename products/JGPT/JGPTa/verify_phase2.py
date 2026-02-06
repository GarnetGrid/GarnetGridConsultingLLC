import asyncio
import json
import httpx

API_URL = "http://localhost:8000/chat"

async def test_streaming():
    payload = {
        "message": "What is CALCULATE in DAX? Search the web if needed.",
        "persona": "powerbi",
        "model": "llama3.2",
        "grade": True
    }
    
    print(f"Sending request to {API_URL}...")
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream("POST", API_URL, json=payload) as response:
                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    print(await response.aread())
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        type_ = data.get("type", "unknown")
                        if type_ == "metadata":
                            print(f"[METADATA] Citations: {len(data.get('citations', []))}")
                        elif type_ == "thought":
                            print(f"[THOUGHT] {data.get('text')}")
                        elif type_ == "tool":
                            print(f"[TOOL] {data.get('name')} input: {data.get('input')}")
                        elif type_ == "answer":
                            print(f"[ANSWER] {data.get('chunk')}", end="", flush=True)
                        elif type_ == "done":
                            print(f"\n[DONE] Quality: {data.get('quality')}")
    except Exception as e:
        print(f"Connection failed (is the server running?): {e}")

if __name__ == "__main__":
    asyncio.run(test_streaming())
