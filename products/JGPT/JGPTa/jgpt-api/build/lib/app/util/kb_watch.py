from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from app.util.ingest import ingest_kb, KB_ROOT

@dataclass
class KBWatchState:
    last_fingerprint: str = ""
    last_run_ok: bool = True
    last_run_error: str = ""
    last_run_ts: float = 0.0
    runs: int = 0

STATE = KBWatchState()

def _fingerprint_kb(root: Path) -> str:
    # Cheap fingerprint: (path, mtime, size) for all files
    parts = []
    for fp in sorted(root.rglob("*")):
        if not fp.is_file():
            continue
        try:
            st = fp.stat()
            parts.append(f"{fp.as_posix()}|{int(st.st_mtime)}|{st.st_size}")
        except FileNotFoundError:
            continue
    return str(hash("\n".join(parts)))

async def maybe_reload_kb(force: bool = False) -> dict:
    root = KB_ROOT
    if not root.exists():
        return {"ok": False, "error": f"KB_ROOT not found: {root}"}
    fp = _fingerprint_kb(root)
    if (not force) and fp == STATE.last_fingerprint:
        return {"ok": True, "changed": False, "runs": STATE.runs}
    try:
        report = await ingest_kb()
        STATE.last_fingerprint = fp
        STATE.last_run_ok = True
        STATE.last_run_error = ""
        STATE.last_run_ts = asyncio.get_event_loop().time()
        STATE.runs += 1
        return {"ok": True, "changed": True, "report": report, "runs": STATE.runs}
    except Exception as e:
        STATE.last_run_ok = False
        STATE.last_run_error = str(e)
        STATE.last_run_ts = asyncio.get_event_loop().time()
        STATE.runs += 1
        return {"ok": False, "changed": True, "error": str(e), "runs": STATE.runs}

async def kb_watch_loop(poll_seconds: int = 10) -> None:
    # enable with KB_WATCH=1
    while True:
        try:
            await maybe_reload_kb(force=False)
        except Exception:
            pass
        await asyncio.sleep(poll_seconds)

def kb_watch_enabled() -> bool:
    return os.getenv("KB_WATCH", "0").strip() in ("1","true","yes","on")
