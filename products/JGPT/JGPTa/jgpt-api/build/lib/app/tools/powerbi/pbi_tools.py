from __future__ import annotations
import json
from typing import Dict, Any, List

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Power BI Model Tools."""
    action = inp.get("action", "parse_schema")
    
    if action == "parse_schema":
        return parse_schema(inp)
    elif action == "data_dictionary":
        return generate_data_dictionary(inp)
    elif action == "calc_group_scaffold":
        return scaffold_calculation_group(inp)
    elif action == "measure_lineage":
        return get_measure_lineage(inp)
    elif action == "detailed_dictionary":
        return generate_detailed_dictionary(inp)
    else:
        return {"error": f"Unknown action: {action}"}

def parse_schema(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a .bim file content and returns a summarized schema."""
    bim_content = inp.get("bim_content", "{}")
    try:
        data = json.loads(bim_content) if isinstance(bim_content, str) else bim_content
        model = data.get("model", {})
        tables = model.get("tables", [])
        
        summary = []
        for table in tables:
            t_name = table.get("name")
            cols = [c.get("name") for c in table.get("columns", [])]
            measures = [m.get("name") for m in table.get("measures", [])]
            summary.append({
                "table": t_name,
                "column_count": len(cols),
                "measure_count": len(measures),
                "measures": measures[:10]  # Limit for context
            })
            
        return {
            "tool": "powerbi.schema_parser",
            "table_count": len(tables),
            "summary": summary,
            "relationships": len(model.get("relationships", []))
        }
    except Exception as e:
        return {"error": f"Failed to parse BIM: {str(e)}"}

def generate_data_dictionary(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a markdown data dictionary from a parsed schema."""
    summary = inp.get("summary", [])
    md = "# Power BI Data Dictionary\n\n"
    for item in summary:
        md += f"## Table: {item['table']}\n"
        md += f"- Columns: {item['column_count']}\n"
        md += f"- Measures: {', '.join(item['measures'])}{'...' if item['measure_count'] > 10 else ''}\n\n"
    
    return {
        "tool": "powerbi.data_dictionary",
        "markdown": md
    }

def scaffold_calculation_group(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Returns a template for a Time Intelligence Calculation Group."""
    group_name = inp.get("name", "Time Intelligence")
    items = [
        {"name": "Current", "expression": "SELECTEDMEASURE()"},
        {"name": "YTD", "expression": "TOTALYTD(SELECTEDMEASURE(), 'Date'[Date])"},
        {"name": "YoY %", "expression": "VAR __prev = CALCULATE(SELECTEDMEASURE(), SAMEPERIODLASTYEAR('Date'[Date])) RETURN DIVIDE(SELECTEDMEASURE() - __prev, __prev)"}
    ]
    
    return {
        "tool": "powerbi.calc_group_scaffold",
        "group_name": group_name,
        "items": items,
        "instruction": "Import this into Tabular Editor as a new Calculation Group."
    }

def get_measure_lineage(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Finds dependencies between measures based on references in their expressions."""
    bim_content = inp.get("bim_content", "{}")
    try:
        data = json.loads(bim_content) if isinstance(bim_content, str) else bim_content
        model_inner = data.get("model", {})
        tables = model_inner.get("tables", [])
        
        all_measures = {}
        for t in tables:
            for m in t.get("measures", []):
                all_measures[m.get("name")] = {
                    "table": t.get("name"),
                    "expression": m.get("expression", "")
                }
        
        lineage = []
        for name, info in all_measures.items():
            deps = []
            for other_name in all_measures.keys():
                if name != other_name and f"[{other_name}]" in info["expression"]:
                    deps.append(other_name)
            if deps:
                lineage.append({"measure": name, "depends_on": deps})
                
        return {
            "tool": "powerbi.measure_lineage",
            "lineage_count": len(lineage),
            "lineage": lineage
        }
    except Exception as e:
        return {"error": f"Lineage check failed: {str(e)}"}

def generate_detailed_dictionary(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a CSV-style array of all fields and measures."""
    bim_content = inp.get("bim_content", "{}")
    try:
        data = json.loads(bim_content) if isinstance(bim_content, str) else bim_content
        model_inner = data.get("model", {})
        tables = model_inner.get("tables", [])
        
        rows = [["Table", "Name", "Type", "Hidden", "Expression/DataType"]]
        for t in tables:
            t_name = t.get("name")
            for c in t.get("columns", []):
                rows.append([t_name, c.get("name"), "Column", str(c.get("isHidden", False)), c.get("dataType", "unknown")])
            for m in t.get("measures", []):
                rows.append([t_name, m.get("name"), "Measure", str(m.get("isHidden", False)), m.get("expression", "")])
                
        return {
            "tool": "powerbi.detailed_dictionary",
            "row_count": len(rows),
            "data": rows
        }
    except Exception as e:
        return {"error": f"Detailed dictionary failed: {str(e)}"}
