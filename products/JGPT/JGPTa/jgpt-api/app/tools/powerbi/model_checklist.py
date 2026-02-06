from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tool":"powerbi.model_checklist",
        "checklist":[
            "Star schema: facts in center, dimensions one-to-many into facts",
            "Single direction filters unless a justified reason",
            "Mark Date table; use continuous daily column",
            "Avoid bi-directional unless for specific bridging scenarios",
            "Hide surrogate keys in report view; keep friendly columns visible",
        ]
    }
