from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from app.evals.runner import run_eval_suite

router = APIRouter()

class EvalReq(BaseModel):
    suite: str = "default"

@router.post("")
async def run_eval(req: EvalReq):
    try:
        return await run_eval_suite(req.suite)
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=500, content={"error": str(e), "ok": False})


from pathlib import Path
import json, re

@router.get("/latest")
def latest_eval():
    rep_dir = Path(__file__).resolve().parents[2] / "eval" / "reports"
    if not rep_dir.exists():
        return {"ok": False, "error": "No reports directory yet."}
    mds = sorted(rep_dir.glob("report_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    jss = sorted(rep_dir.glob("report_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mds and not jss:
        return {"ok": False, "error": "No reports found."}
    md = mds[0].read_text(encoding="utf-8") if mds else ""
    js = json.loads(jss[0].read_text(encoding="utf-8")) if jss else {}
    return {"ok": True, "markdown": md, "json": js}
