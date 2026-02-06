from __future__ import annotations
from typing import Dict, Any
import re

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    code = inp.get("code", "")
    
    # Try to find while select + update pattern
    # while select forupdate myTable where myTable.Field == 'Value' { myTable.OtherField = 'NewValue'; myTable.update(); }
    
    match = re.search(r"while\s+select\s+forupdate\s+(\w+)\s*(?:where\s+([\s\S]+?))?\s*\{\s*([\s\S]+?)\.update\(\)\s*;\s*\}", code, re.IGNORECASE | re.DOTALL)
    
    if not match:
        return {
            "tool": "d365fo.set_based_wizard",
            "error": "Could not identify a standard 'while select forupdate' loop to refactor. Please ensure it follows the pattern: while select forupdate T { T.Field = X; T.update(); }",
            "detected_code": code
        }
        
    table_var = match.group(1)
    where_clause = match.group(2).strip() if match.group(2) else "/* TODO: Add where clause */"
    inner_logic = match.group(3).strip()
    
    # Extract assignments: T.Field = Value;
    assignments = re.findall(rf"{table_var}\.(\w+)\s*=\s*([^;]+);", inner_logic)
    
    if not assignments:
        return {
             "tool": "d365fo.set_based_wizard",
             "error": "Found the loop but could not extract field assignments.",
             "detected_table": table_var
        }

    setting_lines = []
    for field, val in assignments:
        setting_lines.append(f"    setting {field} = {val.strip()}")
    
    setting_str = ",\n".join(setting_lines)
    
    refactored = f"""update_recordset {table_var}
{setting_str}
where {where_clause};"""

    return {
        "tool": "d365fo.set_based_wizard",
        "original_code": code,
        "refactored_code": refactored,
        "explanation": "Converted row-by-row while select loop into a single SQL-efficient update_recordset statement.",
        "warning": "Ensure that the table's update() method doesn't contain critical logic that must run per-row, as update_recordset bypasses the X++ update() method."
    }
