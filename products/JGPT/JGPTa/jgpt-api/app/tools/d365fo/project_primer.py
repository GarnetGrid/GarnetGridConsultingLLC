from __future__ import annotations
import json
from typing import Dict, Any
from app.db.session import SessionLocal
from app.db.models import PrimedContext

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    project_name = inp.get("project_name", "Default")
    objects = inp.get("objects", [])
    description = inp.get("description", "")
    user_id = inp.get("_user_id")
    
    context = {
        "project_name": project_name,
        "description": description,
        "objects": objects,
        "type": "D365FO"
    }
    
    try:
        if user_id:
            with SessionLocal() as s:
                existing = s.query(PrimedContext).filter_by(user_id=user_id, context_type="d365fo").first()
                if existing:
                    existing.context_data = json.dumps(context)
                else:
                    new_ctx = PrimedContext(user_id=user_id, context_type="d365fo", context_data=json.dumps(context))
                    s.add(new_ctx)
                s.commit()
        else:
            return {"error": "User context required for persistence"}

    except Exception as e:
        return {"error": f"Failed to save context: {str(e)}"}
        
    return {
        "tool": "d365fo.project_primer",
        "status": "success",
        "message": f"Project '{project_name}' primed with {len(objects)} objects.",
        "context_summary": context
    }
