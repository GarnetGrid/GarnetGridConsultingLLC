from __future__ import annotations
import json
from typing import Dict, Any
from app.db.session import SessionLocal
from app.db.models import PrimedContext

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    model_name = inp.get("model_name", "Default Model")
    bim_content = inp.get("bim_content", "{}")
    user_id = inp.get("_user_id")
    
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
        
        if user_id:
            with SessionLocal() as s:
                # Upsert context for user
                existing = s.query(PrimedContext).filter_by(user_id=user_id, context_type="powerbi").first()
                if existing:
                    existing.context_data = json.dumps(context)
                else:
                    new_ctx = PrimedContext(user_id=user_id, context_type="powerbi", context_data=json.dumps(context))
                    s.add(new_ctx)
                s.commit()
        else:
            # Fallback for dev/testing without auth context if needed (though _user_id should be there)
            return {"error": "User context required for persistence"}

    except Exception as e:
        return {"error": f"Failed to prime model: {str(e)}"}
        
    return {
        "tool": "powerbi.model_primer",
        "status": "success",
        "message": f"Model '{model_name}' primed with {len(summary)} tables.",
        "tables_detected": [s["name"] for s in summary]
    }
