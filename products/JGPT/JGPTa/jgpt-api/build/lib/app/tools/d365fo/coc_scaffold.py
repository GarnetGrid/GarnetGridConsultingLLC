from __future__ import annotations
from typing import Dict, Any

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    target_object = inp.get("target_object", "CustTable")
    object_type = inp.get("object_type", "table") # table, class, data_source
    method_name = inp.get("method_name", "insert")
    return_type = inp.get("return_type", "void")
    parameters = inp.get("parameters", "")
    
    # Clean suffix (e.g. remove _Extension if user added it)
    base_name = target_object.split('_')[0]
    class_name = f"{base_name}_JGPT_Extension"
    
    decorator = f"[ExtensionOf({object_type}Str({target_object}))]"
    
    params_str = parameters if parameters else ""
    call_params = ""
    if parameters:
        # Simple heuristic to extract parameter names for the 'next' call
        # e.g. "int _id, str _name" -> "_id, _name"
        parts = [p.strip().split(' ') for p in parameters.split(',')]
        call_params = ", ".join([p[-1] for p in parts if len(p) > 0])

    next_call = f"next {method_name}({call_params});"
    if return_type.lower() != "void":
        next_call = f"{return_type} ret = {next_call}"

    return_stmt = f"\n        return ret;" if return_type.lower() != "void" else ""

    template = f"""{decorator}
final class {class_name}
{{
    /// <summary>
    /// JGPT Scaffolder: Wrapping {method_name} on {target_object}
    /// </summary>
    public {return_type} {method_name}({params_str})
    {{
        // TODO: Add Pre-logic here
        
        {next_call}
        
        // TODO: Add Post-logic here
        {return_stmt}
    }}

}}"""

    return {
        "tool": "d365fo.coc_scaffold",
        "class_name": class_name,
        "code": template,
        "instructions": "Copy this code into a new X++ class file in your development model."
    }
