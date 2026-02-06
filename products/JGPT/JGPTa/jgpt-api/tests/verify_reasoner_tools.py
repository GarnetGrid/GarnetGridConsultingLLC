import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure app is in path
sys.path.append(os.getcwd())

# Mock registry BEFORE importing reasoner to avoid matplotlib/analytics dependency
mock_registry = MagicMock()
mock_registry.TOOLS = {}
sys.modules["app.tools.registry"] = mock_registry

from app.services.reasoner import ReasonerService
# Access the mocked TOOLS dict
from app.tools.registry import TOOLS

async def mock_tool_func(args):
    return f"Mocked outcome for {args}"

async def run_tests():
    print("--- Testing Reasoner Tool Execution ---")
    
    # 1. Inject a mock tool
    TOOLS["mock_weather"] = mock_tool_func
    
    # 2. Mock Ollama to return a JSON action
    with patch("app.services.reasoner.ollama_chat") as mock_chat:
        # Mock response for execute_step
        mock_chat.return_value = '```json\n{"action": {"name": "mock_weather", "input": {"location": "NYC"}}}\n```'
        
        # Reasoner picks tools internally, but we mocked pick_tools?
        # Actually execute_step calls pick_tools. We need to patch that too.
        with patch("app.services.reasoner.pick_tools") as mock_pick:
            mock_pick.return_value = [{"name": "mock_weather", "description": "Get weather"}]
            
            svc = ReasonerService(model="test-model")
            
            # Test execute_step
            print("Invoking execute_step('Check weather in NYC')...")
            result = await svc.execute_step("Check weather in NYC")
            
            print(f"Result: {result}")
            
            if "Mocked outcome" in result and "NYC" in result:
                print("✅ SUCCESS: Tool was called and result returned.")
            else:
                print(f"❌ FAILED: Unexpected result: {result}")

    # 3. Clean up
    if "mock_weather" in TOOLS:
        del TOOLS["mock_weather"]

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except Exception as e:
        print(f"Test crashed: {e}")
