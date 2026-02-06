import asyncio
import sys
import os

# Add parent dir to path to find app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.local_llm.ollama_client import OllamaClient

async def main():
    print("Testing DeepSeek Connection via Ollama...")
    client = OllamaClient()
    
    available = await client.is_available()
    if available:
        print("[OK] Ollama is online.")
    else:
        print("[FAIL] Ollama is unavailable. Ensure it is running at localhost:11434")
        return

    prompt = "Write a python function to add two numbers."
    print(f"\nSending prompt: {prompt}")
    
    response = await client.generate_completion(prompt)
    if response:
        print("\n[SUCCESS] Response received:")
        print("-" * 40)
        print(response)
        print("-" * 40)
    else:
        print("\n[FAIL] No response received or error occurred.")

if __name__ == "__main__":
    asyncio.run(main())
