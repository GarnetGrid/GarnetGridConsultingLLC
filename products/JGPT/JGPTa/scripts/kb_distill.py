#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import argparse
from pathlib import Path
import asyncio
import httpx

BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
MODEL = os.getenv("KB_DISTILL_MODEL", os.getenv("CHAT_MODEL", "llama3.2"))

SYSTEM = """You are an expert technical writer creating retrieval-friendly knowledge base (KB) cards.
Output MUST be markdown.
Make compact “pattern cards” with headings, bullets, and code blocks.
Avoid copying large verbatim passages; summarize and produce templates.
Include: Problem, When to use, Steps, Code, Common mistakes, Variants (if applicable).
"""

PROMPT_TMPL = """Create 6-10 KB pattern cards for domain: {domain}.

Source document filename: {name}

Source content:
{content}

Return markdown only.
"""

async def ollama_chat(system: str, user: str) -> str:
    payload = {"model": MODEL, "messages":[{"role":"system","content":system},{"role":"user","content":user}], "stream": False}
    async with httpx.AsyncClient(timeout=180.0) as client:
        r = await client.post(f"{BASE}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    return ((data.get("message") or {}).get("content")) or ""

def iter_sources(src_dir: Path):
    for p in src_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".md",".txt"):
            yield p

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", choices=["powerbi","d365fo","all"], default="all")
    ap.add_argument("--sources-root", default="jgpt-api/kb/_sources")
    ap.add_argument("--out-root", default="jgpt-api/kb")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    sources_root = (repo_root / args.sources_root).resolve()
    out_root = (repo_root / args.out_root).resolve()

    domains = ["powerbi","d365fo"] if args.domain == "all" else [args.domain]

    for dom in domains:
        src_dir = sources_root / dom
        if not src_dir.exists():
            continue
        out_dir = out_root / dom / "packs"
        out_dir.mkdir(parents=True, exist_ok=True)

        for p in iter_sources(src_dir):
            content = p.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue
            user = PROMPT_TMPL.format(domain=dom, name=p.name, content=content[:12000])
            md = await ollama_chat(SYSTEM, user)
            if not md.strip():
                continue
            out_path = out_dir / f"{p.stem}_cards.md"
            out_path.write_text(md.strip() + "\n", encoding="utf-8")
            print(f"Wrote: {out_path.relative_to(repo_root)}")

if __name__ == "__main__":
    asyncio.run(main())
