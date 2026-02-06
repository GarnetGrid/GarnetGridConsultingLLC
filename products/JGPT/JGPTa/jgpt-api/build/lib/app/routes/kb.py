from __future__ import annotations
from fastapi import APIRouter
from app.util.kb_watch import maybe_reload_kb, STATE

router = APIRouter()

@router.get("/status")
def status():
    return {
        "ok": True,
        "runs": STATE.runs,
        "last_run_ok": STATE.last_run_ok,
        "last_run_error": STATE.last_run_error,
        "last_run_ts": STATE.last_run_ts,
    }

@router.post("/reload")
async def reload():
    return await maybe_reload_kb(force=True)
