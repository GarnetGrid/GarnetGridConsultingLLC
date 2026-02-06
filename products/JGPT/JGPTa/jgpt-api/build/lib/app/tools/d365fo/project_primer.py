from __future__ import annotations
import json
import os
from typing import Dict, Any

CONTEXT_FILE = "project_context.json"

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    project_name = inp.get("project_name", "Default")
    objects = inp.get("objects", [])
    description = inp.get("description", "")
    
    context = {
        "project_name": project_name,
        "description": description,
        "objects": objects,
        "type": "D365FO"
    }
    
    # In a real app, this would be in a DB or user-specific storage
    # For now, we'll use a local json file as a mock persistent store
    try:
        with open(CONTEXT_FILE, "w") as f:
            json.dump(context, f, indent=2)
    except Exception as e:
        return {"error": f"Failed to save context: {str(e)}"}
        
    return {
        "tool": "d365fo.project_primer",
        "status": "success",
        "message": f"Project '{project_name}' primed with {len(objects)} objects.",
        "context_summary": context
    }
