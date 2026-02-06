import asyncio
import sys
import os

# Ensure app is in path
sys.path.append(os.getcwd())

from app.services.reasoner import ReasonerService

async def test_decomposition():
    print("--- Testing Decomposition ---")
    svc = ReasonerService()
    query = "Analyze the sales trend for Q1 2024 vs Q1 2023 and identify top 3 drivers of change."
    
    print(f"Query: {query}")
    try:
        steps = await svc.decompose(query)
        print(f"Result (Steps): {steps}")
        
        if len(steps) > 1:
            print("✅ SUCCESS: Query decomposed into multiple steps.")
        else:
            print("⚠️ WARNING: Query was not decomposed (returned 1 step).")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")

async def test_synthesis():
    print("\n--- Testing Synthesis ---")
    svc = ReasonerService()
    query = "Why did sales drop?"
    results = [
        "market_analysis tool shows consumer confidence dropped by 10%.", 
        "competitor_tracker tool shows Competitor X released a cheaper product."
    ]
    try:
        ans = await svc.synthesize(query, results)
        print(f"Result (Synthesis): {ans}")
        if len(ans) > 10:
             print("✅ SUCCESS: Synthesis returned a substantial answer.")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_decomposition())
    asyncio.run(test_synthesis())
