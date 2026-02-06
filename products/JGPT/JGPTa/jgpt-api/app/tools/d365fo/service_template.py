from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    name = inp.get("name","MyService")
    return {
        "tool":"d365fo.service_template",
        "xpp": f"""[SysEntryPointAttribute(true)]
public class {name}
{{
    public void run()
    {{
        // TODO: implement
    }}
}}
""",
        "notes":[
            "Add data contracts for complex parameters.",
            "Use SysEntryPointAttribute for security checks.",
        ]
    }
