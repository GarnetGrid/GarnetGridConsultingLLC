from __future__ import annotations
import os, json, asyncio
from datetime import datetime
from pathlib import Path
import httpx
from app.evals.judge import judge_answer

EVAL_ROOT = Path(__file__).resolve().parents[2] / "eval"

async def run_eval_suite(suite: str = "default") -> dict:
    # expects eval/{powerbi,d365fo}/questions.jsonl
    out = {"suite": suite, "runs": []}
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    files = [
        ("powerbi", EVAL_ROOT / "powerbi" / "questions.jsonl"),
        ("d365fo", EVAL_ROOT / "d365fo" / "questions.jsonl"),
    ]
    async with httpx.AsyncClient(timeout=180.0) as client:
        for mode, fp in files:
            if not fp.exists():
                continue
            for line in fp.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                q = obj["question"]
                ans = ""
                async with client.stream("POST", f"{base_url}/chat", json={"persona": mode, "message": q}) as response:
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        try:
                            data = json.loads(line[6:])
                        except Exception:
                            continue

                        # SSE schema from /chat:
                        # {"type":"answer","chunk":"..."}
                        if data.get("type") == "answer":
                            ans += data.get("chunk") or ""
                judged = await judge_answer(mode, q, ans)
                out["runs"].append({"mode": mode, "question": q, "answer": ans, "judge": judged})
    
    # Save reports
    rep_dir = EVAL_ROOT / "reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = rep_dir / f"report_{timestamp}.json"
    json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    
    # Simple markdown table
    md = f"# Eval Report: {suite}\nDate: {datetime.now().isoformat()}\n\n"
    md += "| Mode | Question | Grade | Score |\n|---|---|---|---|\n"
    for r in out["runs"]:
        g = r["judge"].get("grade", "N/A")
        s = f"{r['judge'].get('total',0)}/{r['judge'].get('max',0)}"
        md += f"| {r['mode']} | {r['question']} | {g} | {s} |\n"
    
    md_path = rep_dir / f"report_{timestamp}.md"
    md_path.write_text(md, encoding="utf-8")
    
    return out
