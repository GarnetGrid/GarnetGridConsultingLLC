from __future__ import annotations
import re
from typing import Dict, Any, List

def run(inp: Dict[str, Any] | str) -> Dict[str, Any]:
    """Main entry point for D365FO Metadata & Performance Tools."""
    if isinstance(inp, str):
        # Fallback for when LLM passes a string directly (hallucination or simpler model behavior)
        # We assume they meant metadata_lookup for a table entity if it's a simple string
        return {"error": "Input must be a JSON object, but received a string.", "received": inp}

    action = inp.get("action", "metadata_lookup")
    
    if action == "metadata_lookup":
        return metadata_lookup(inp)
    elif action == "trace_parser":
        return trace_parser(inp)
    elif action == "sysoperation_scaffold":
        return scaffold_sysoperation(inp)
    else:
        return {"error": f"Unknown action: {action}"}

def metadata_lookup(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Simulates a lookup of D365FO table metadata."""
    table_name = inp.get("table_name", "CustTable")
    # Mock metadata database
    mock_db = {
        "CustTable": {"label": "Customers", "extensible": "Yes", "index_count": 5},
        "SalesTable": {"label": "Sales orders", "extensible": "Yes", "index_count": 8},
        "InventTrans": {"label": "Inventory transactions", "extensible": "No", "index_count": 12}
    }
    
    data = mock_db.get(table_name, {"error": "Table not found in metadata cache."})
    return {
        "tool": "d365fo.metadata_lookup",
        "table": table_name,
        "details": data
    }

def trace_parser(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes trace output for long-running SQL queries correlated to X++."""
    trace_text = inp.get("trace_text", "")
    # Find patterns like: SQL statement: SELECT ... (Time: 5000ms)
    matches = re.findall(r"SQL statement: (.*?) \(Time: (\d+)ms\)", trace_text)
    
    bottlenecks = []
    for sql, time in matches:
        if int(time) > 1000:
            bottlenecks.append({"query": sql[:100] + "...", "duration_ms": int(time)})
            
    return {
        "tool": "d365fo.trace_parser",
        "bottlenecks": bottlenecks,
        "suggestion": "Check missing indexes or excessive join depth on high-duration queries."
    }

def scaffold_sysoperation(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Generates the SysOperation framework boilerplate."""
    base_name = inp.get("base_name", "MyProcess")
    return {
        "tool": "d365fo.sysoperation_scaffold",
        "components": [
            {"file": f"{base_name}Contract.xpp", "summary": "Data member definitions."},
            {"file": f"{base_name}Service.xpp", "summary": "Process logic (SysOperationServiceBase)."},
            {"file": f"{base_name}Controller.xpp", "summary": "Execution management."},
            {"file": f"{base_name}UIBuilder.xpp", "summary": "Custom parameter dialog logic."}
        ]
    }
