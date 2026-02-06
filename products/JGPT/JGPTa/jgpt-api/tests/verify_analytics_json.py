import json
import sys
import os

# Ensure path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock
mock_lib = MagicMock()
sys.modules["matplotlib"] = mock_lib
sys.modules["matplotlib.pyplot"] = mock_lib
sys.modules["seaborn"] = mock_lib

from app.tools.analytics import run_generate_chart

def test_chart_json():
    print("--- Verifying Analytics JSON Output ---")
    
    inp = {
        "chart_type": "bar",
        "title": "Test Sales",
        "x": "month",
        "y": "val",
        "data": [
            {"month": "Jan", "val": 10},
            {"month": "Feb", "val": 20}
        ]
    }
    
    res = run_generate_chart(inp)
    
    if "error" in res:
        print(f"FAILED: Tool returned error: {res['error']}")
        sys.exit(1)
        
    if res.get("type") != "chart_data":
        print(f"FAILED: Expected type 'chart_data', got {res.get('type')}")
        sys.exit(1)
        
    config = res.get("chart_config", {})
    if config.get("type") != "bar" or config.get("title") != "Test Sales":
        print(f"FAILED: Config mismatch: {config}")
        sys.exit(1)
        
    print("SUCCESS: Tool returns valid chart config JSON.")

if __name__ == "__main__":
    test_chart_json()
