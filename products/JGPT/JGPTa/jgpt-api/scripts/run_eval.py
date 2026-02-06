#!/usr/bin/env python3
from __future__ import annotations
import os, json, asyncio
from pathlib import Path
from app.evals.runner import run_eval_suite

async def main():
    suite = os.getenv("EVAL_SUITE","default")
    result = await run_eval_suite(suite)

    out_dir = Path("eval") / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"report_{ts}.json"
    md_path = out_dir / f"report_{ts}.md"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    # simple markdown render
    lines = [f"# JGPT Eval Report ({ts})", ""]
    for run in result.get("runs", []):
        mode = run["mode"]
        judge = run.get("judge", {})
        total = judge.get("total", 0)
        maxv = judge.get("max", 0)
        lines += [f"## {mode} — {total}/{maxv}", "", f"**Q:** {run['question']}", "", f"**A:**", "```", run['answer'][:4000], "```", ""]
        for item in judge.get("items", []):
            lines.append(f"- {item.get('score')}/2 — {item.get('criterion')}: {item.get('notes','')}")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {json_path} and {md_path}")

if __name__ == "__main__":
    asyncio.run(main())
