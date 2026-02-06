from __future__ import annotations
from typing import Dict, Any
import re

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    code = inp.get("code", "")
    issues = []

    # 1. Transaction Hygiene
    if "ttsBegin" in code and "ttsAbort" not in code:
        issues.append("[CRITICAL] Transaction level risk: Found ttsBegin without matching ttsAbort in a catch block. This can leak ttsLevel and cause system-wide instability.")
    
    # 2. Set-Based Opportunities (The most common Junior mistake)
    if re.search(r"while\s+select\s+.*\{\s*.*\bupdate\(\)\s*;", code, re.IGNORECASE | re.DOTALL):
        issues.append("[PERFORMANCE] Set-based Opportunity: Found a while select loop calling update(). Use update_recordset for 10x+ performance gains.")
    
    if re.search(r"while\s+select\s+.*\{\s*.*\binsert\(\)\s*;", code, re.IGNORECASE | re.DOTALL):
        issues.append("[PERFORMANCE] Set-based Opportunity: Found a while select loop calling insert(). Use insert_recordset to avoid unnecessary row-by-row SQL roundtrips.")

    # 3. Performance Hints
    if re.search(r"\bselect\s+(?!firstOnly)\b", code, re.IGNORECASE):
        if "while" not in code.lower() and "join" not in code.lower():
             issues.append("[TIP] Potential missing firstOnly: If you only need one record (e.g. for existence check), specify firstOnly to stop the SQL kernel early.")

    # 4. Security Patterns
    if "curUserId()" in code or "\"Admin\"" in code:
         issues.append("[SECURITY] Hardcoded User Check: Avoid curUserId() == \"Admin\". Use SecurityRights or check for specific functional Privileges instead.")

    # 5. Data Entity Anti-Patterns
    if "postLoad" in code and ("DataEntity" in code or "Entity" in code):
        issues.append("[ARCHITECTURE] Entity Performance: postLoad logic detected. If this is for a field calculation, use a Computed Column (T-SQL) instead of a Virtual Field (X++) for OData efficiency.")

    # 6. crossCompany Efficiency
    if "crossCompany" in code.lower() and "container" not in code.lower():
        issues.append("[PERFORMANCE] crossCompany without container: You are querying across all companies. If you know the target legal entities, pass a container to crossCompany to reduce SQL index scan overhead.")

    # 7. Date-Effective (validTimeState)
    date_effective_tables = ["HcmEmployment", "DirPartyLocation", "OmInternalOrganization"]
    for tbl in date_effective_tables:
        if tbl.lower() in code.lower() and "validTimeState" not in code:
            issues.append(f"[BUG/PERFORMANCE] Missing validTimeState: {tbl} is a date-effective table. Querying it without validTimeState(date) or validTimeState(startDate, endDate) will only return currently active records, which might be a bug, and bypasses interval optimization.")

    # 8. SQL Injection / Hardcoded Strings
    if "strFmt" in code and ("where" in code or "select" in code) and ("%1" in code):
        # Very loose check for dynamic SQL construction
        issues.append("[SECURITY] Dynamic SQL Risk: Detected use of strFmt in a query-like context. Use SysQuery::value() or query parameters to prevent SQL injection.")

    return {
        "tool": "d365fo.xpp_lint",
        "issue_count": len(issues),
        "issues": issues,
        "recommendation": "Review the flagged items above. Prioritize Set-Based refactoring and Transaction hygiene." if issues else "Code looks Senior-grade! No major anti-patterns detected."
    }
