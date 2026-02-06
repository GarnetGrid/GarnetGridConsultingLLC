from __future__ import annotations

import json
import os
import httpx

TOOL_CHOICES = [
    "powerbi.context_debugger",
    "powerbi.trailing_weeks_generator",
    "powerbi.dax_lint",
    "powerbi.pbi_tools",
    "powerbi.star_schema_validator",
    "d365fo.tts_template",
    "d365fo.coc_vs_events",
    "d365fo.xpp_lint",
    "d365fo.service_template",
    "d365fo.d365_metadata",
    "d365fo.coc_scaffold",
    "d365fo.set_based_wizard",
    "d365fo.project_primer",
    "powerbi.model_primer",
    "web_search",
    "save_snippet",
    "kb_search",
    "sql.list_connections", 
    "sql.get_schema", 
    "sql.query",
    "sql.add_connection",
    "sql.delete_connection",
    "memory.remember_fact",
    "memory.remember_entity",
    "memory.list_facts",
    "memory.delete_fact",
    "memory.search_history",
    "analytics.generate_plot",
    "scaffold.template",
]

async def pick_tools(mode: str, message: str, history: list[dict] = None) -> list[dict]:
    """Ask the chat model to pick up to 3 helpful tools.
    Returns a list like: [{"name": "...", "input": {...}}, ...]
    If routing fails, returns [].
    """
    base = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    model = os.getenv("CHAT_MODEL", "llama3.2")

    system = (
        "You are a strategic tool router. Choose up to 3 tools from the allowed list that would help answer the user. "
        "Consider the conversation history to understand the user's intent and any previous tool results. "
        "If the user has a complex task, pick tools that can work together (e.g., metadata lookup and linting). "
        "Return STRICT JSON only, with this shape: "
        "{\"tools\":[{\"name\":\"tool.name\",\"input\":{}}]} "
        "No markdown, no commentary."
    )

    # Simplified history for the router (last 3 turns)
    recent_history = history[-6:] if history else []
    
    user_obj = {
        "mode": mode, 
        "message": message, 
        "history_context": recent_history,
        "allowed_tools": TOOL_CHOICES
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_obj)},
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.post(f"{base}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []

    content = ((data.get("message") or {}).get("content")) or ""
    try:
        obj = json.loads(content)
        tools = obj.get("tools") or []
        if not isinstance(tools, list):
            return []

        cleaned: list[dict] = []
        for t in tools[:3]:
            name = t.get("name")
            if name in TOOL_CHOICES:
                cleaned.append({"name": name, "input": t.get("input") or {}})
        return cleaned
    except Exception:
        return []
