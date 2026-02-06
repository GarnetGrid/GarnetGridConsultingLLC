from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "tool":"d365fo.coc_vs_events",
        "summary":[
            "Chain of Command (CoC): wraps a method; you can call next. Great for modifying behavior in-line.",
            "Event handlers: subscribe to pre/post events; more decoupled, but can be harder to trace.",
            "Upgradability: both are upgrade-safe vs overlayering; CoC depends on method being CoC-enabled.",
            "Performance: excessive event handlers can add overhead; CoC is typically tighter but still adds call layers."
        ],
        "decision_rule":"Use CoC when you must change a specific method’s logic. Use events for cross-cutting, optional behavior."
    }
