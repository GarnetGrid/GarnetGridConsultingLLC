from __future__ import annotations
from typing import Dict, Any, List
import json

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    bim_content = inp.get("bim_content", "")
    if not bim_content:
        return {"tool": "powerbi.star_schema_validator", "error": "No .bim content provided."}
    
    try:
        model = json.loads(bim_content)
    except Exception:
        return {"tool": "powerbi.star_schema_validator", "error": "Invalid .bim format. Ensure it is valid JSON."}
    
    issues: List[str] = []
    tables = model.get("model", {}).get("tables", [])
    
    # 1. Bi-directional Filter Check
    for table in tables:
        for rel in model.get("model", {}).get("relationships", []):
            if rel.get("crossFilteringBehavior") == "bothDirections":
                from_tbl = rel.get("fromTable")
                to_tbl = rel.get("toTable")
                issues.append(f"[PERFORMANCE] Bi-directional filter found between {from_tbl} and {to_tbl}. This causes ambiguity and performance bottlenecks in large models. Use cross-filtering only when strictly necessary for specific measure logic via CROSSFILTER.")

    # 2. Snowflake vs Star Schema Check (Simplified)
    # If a table is joined to another table that is NOT a fact table (heuristic)
    # This is complex without knowing table roles, but we can look for many-to-many or long chains.
    
    # 3. Hidden Fields check
    for table in tables:
        hidden_count = sum(1 for col in table.get("columns", []) if col.get("isHidden"))
        total_cols = len(table.get("columns", []))
        if total_cols > 0 and (hidden_count / total_cols) < 0.1:
             issues.append(f"[UX] Low hidden field ratio in {table.get('name')}: Only {hidden_count}/{total_cols} fields are hidden. Senior architects hide all foreign keys and raw transaction fields to improve the end-user experience.")

    # 4. Referential Integrity
    for rel in model.get("model", {}).get("relationships", []):
        if rel.get("relyOnReferentialIntegrity"):
             issues.append(f"[VALIDATION] Relationship between {rel.get('fromTable')} and {rel.get('toTable')} uses 'Assume Referential Integrity'. Ensure the database source enforces these constraints to avoid incorrect data aggregation.")

    return {
        "tool": "powerbi.star_schema_validator",
        "issue_count": len(issues),
        "issues": issues,
        "recommendation": "Address bi-directional filters first as they are the highest performance risk." if issues else "Model looks architect-grade!"
    }
