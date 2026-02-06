from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
from app.tools.registry import TOOLS
from app.util.auth import get_current_user
from app.db.models import User

router = APIRouter()

class ToolExecutionRequest(BaseModel):
    tool_name: str
    input: Dict[str, Any]

@router.post("/execute")
async def execute_tool(req: ToolExecutionRequest, current_user: User = Depends(get_current_user)):
    """Executes a tool directly."""
    if req.tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool {req.tool_name} not found")
    
    tool_fn = TOOLS[req.tool_name]
    try:
        import inspect
        if inspect.iscoroutinefunction(tool_fn):
            # Inject user_id into input for context-aware tools
            # We treat keys starting with _ as system/internal parameters
            safe_input = req.input.copy()
            safe_input["_user_id"] = current_user.id
            result = await tool_fn(safe_input)
        else:
            from fastapi.concurrency import run_in_threadpool
            safe_input = req.input.copy()
            safe_input["_user_id"] = current_user.id
            result = await run_in_threadpool(tool_fn, safe_input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_tools(current_user: User = Depends(get_current_user)):
    """Returns a list of all available tools."""
    return {
        "tools": [{"name": name} for name in TOOLS.keys()]
    }
