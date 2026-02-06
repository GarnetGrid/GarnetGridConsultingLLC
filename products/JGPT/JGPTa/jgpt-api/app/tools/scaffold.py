import shutil
import os
from typing import Dict, Any

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

AVAILABLE_TEMPLATES = {
    "charter": "project_charter.md",
    "requirements": "requirements.md",
    "design": "tech_design.md",
    "test_plan": "test_plan.md",
    "user_guide": "user_guide.md"
}

def run_scaffold_template(inp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scaffolds a documentation template into the user's workspace.
    
    Args:
        inp: {
            "template_name": str ("charter", "requirements", "design", "test_plan", "user_guide"),
            "target_filename": str (Optional: Defaults to the template name),
            "target_dir": str (Optional: relative path, defaults to current directory or 'docs')
        }
    """
    template_key = inp.get("template_name", "").lower()
    target_filename = inp.get("target_filename")
    target_dir = inp.get("target_dir", ".")
    
    if template_key not in AVAILABLE_TEMPLATES:
        return {
            "error": f"Template '{template_key}' not found. Available: {list(AVAILABLE_TEMPLATES.keys())}",
            "available_templates": list(AVAILABLE_TEMPLATES.keys())
        }
        
    source_file = AVAILABLE_TEMPLATES[template_key]
    source_path = os.path.join(TEMPLATE_DIR, source_file)
    
    if not os.path.exists(source_path):
        return {"error": f"System Configuration Error: Template file {source_file} missing at {source_path}"}
        
    # Determine final path
    final_filename = target_filename or source_file
    # If target_dir is absolute, use it. If relative, assume relative to PWD (which inside docker is /app)
    # Ideally, we want to write to the bind-mounted volume so user sees it.
    # IN DOCKER: /app is the root.
    
    final_path = os.path.join(target_dir, final_filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(final_path) or ".", exist_ok=True)
    
    try:
        shutil.copy(source_path, final_path)
        return {
            "status": "success",
            "message": f"Created {final_filename} from {template_key} template.",
            "path": final_path,
            "content_preview": open(final_path, 'r').read()[:200]
        }
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}
