from __future__ import annotations
import json
import os
from typing import Dict, Any

MODEL_CONTEXT_FILE = "model_context.json"

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    model_name = inp.get("model_name", "Default Model")
    bim_content = inp.get("bim_content", "{}")
    
    try:
        data = json.loads(bim_content) if isinstance(bim_content, str) else bim_content
        model_inner = data.get("model", {})
        tables = model_inner.get("tables", [])
        
        summary = []
        for t in tables:
            summary.append({
                "name": t.get("name"),
                "columns": [c.get("name") for c in t.get("columns", [])],
                "measures": [m.get("name") for m in t.get("measures", [])]
            })
            
        context = {
            "model_name": model_name,
            "table_summary": summary,
            "type": "PowerBI"
        }
        
        with open(MODEL_CONTEXT_FILE, "w") as f:
            json.dump(context, f, indent=2)
            
    except Exception as e:
        return {"error": f"Failed to prime model: {str(e)}"}
        
    return {
        "tool": "powerbi.model_primer",
        "status": "success",
        "message": f"Model '{model_name}' primed with {len(summary)} tables.",
        "tables_detected": [s["name"] for s in summary]
    }
