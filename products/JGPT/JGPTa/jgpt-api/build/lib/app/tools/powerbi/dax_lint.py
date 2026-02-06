from __future__ import annotations
from typing import Dict, Any
import re

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    dax = inp.get("dax","")
    issues = []
    if "ALL(" in dax and "FILTER(" in dax:
        issues.append("ALL + FILTER can be expensive; consider KEEPFILTERS or variables for readability.")
    if re.search(r"\bEARLIER\b", dax, re.IGNORECASE):
        issues.append("EARLIER is usually a smell; prefer variables or CALCULATE patterns.")
    if re.search(r"\bSUM\s*\(", dax) and re.search(r"\bSUMX\s*\(", dax):
        issues.append("Mixing SUM and SUMX can be correct, but double-check granularity.")
    return {"tool":"powerbi.dax_lint","issue_count":len(issues),"issues":issues}
