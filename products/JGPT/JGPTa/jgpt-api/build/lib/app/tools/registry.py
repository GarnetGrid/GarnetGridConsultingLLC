from __future__ import annotations
from typing import Callable, Dict, Any

from app.tools.powerbi.context_debugger import run as powerbi_context_debugger
from app.tools.powerbi.trailing_weeks_generator import run as powerbi_trailing_weeks
from app.tools.powerbi.dax_lint import run as powerbi_dax_lint
from app.tools.powerbi.model_checklist import run as powerbi_model_checklist
from app.tools.powerbi.pbi_tools import run as powerbi_pbi_tools
from app.tools.powerbi.star_schema_validator import run as powerbi_star_schema_validator

from app.tools.d365fo.tts_template import run as d365_tts_template
from app.tools.d365fo.coc_vs_events import run as d365_coc_vs_events
from app.tools.d365fo.xpp_lint import run as d365_xpp_lint
from app.tools.d365fo.service_template import run as d365_service_template
from app.tools.d365fo.d365_metadata import run as d365_metadata
from app.tools.d365fo.coc_scaffold import run as d365_coc_scaffold
from app.tools.d365fo.set_based_wizard import run as d365_set_based_wizard
from app.tools.d365fo.project_primer import run as d365_project_primer
from app.tools.powerbi.model_primer import run as powerbi_model_primer
from app.tools.powerbi.dax_guard import run as powerbi_dax_guard
from app.tools.web_search import web_search
from app.tools.exporter import save_snippet
from app.tools.kb_search import run as kb_search


def save_snippet_tool(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Tool wrapper for save_snippet.

    The agent tool interface expects a single dict input.
    """
    title = (inp or {}).get("title") or "Untitled"
    content = (inp or {}).get("content") or ""
    category = (inp or {}).get("category") or "general"
    fmt = (inp or {}).get("format") or "md"
    try:
        result = save_snippet(title, content, category=category, format=fmt)
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}

TOOLS: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
  "powerbi.context_debugger": powerbi_context_debugger,
  "powerbi.trailing_weeks_generator": powerbi_trailing_weeks,
  "powerbi.dax_lint": powerbi_dax_lint,
  "powerbi.model_checklist": powerbi_model_checklist,
  "powerbi.pbi_tools": powerbi_pbi_tools,
  "powerbi.star_schema_validator": powerbi_star_schema_validator,
  "d365fo.tts_template": d365_tts_template,
  "d365fo.coc_vs_events": d365_coc_vs_events,
  "d365fo.xpp_lint": d365_xpp_lint,
  "d365fo.service_template": d365_service_template,
  "d365fo.d365_metadata": d365_metadata,
  "d365fo.coc_scaffold": d365_coc_scaffold,
  "d365fo.set_based_wizard": d365_set_based_wizard,
  "d365fo.project_primer": d365_project_primer,
  "powerbi.model_primer": powerbi_model_primer,
  "web_search": web_search,
  "save_snippet": save_snippet_tool,
  "kb_search": kb_search,
}