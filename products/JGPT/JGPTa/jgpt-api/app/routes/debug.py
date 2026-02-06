from __future__ import annotations

import os
import httpx
from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import SessionLocal
from app.db.models import Document, Chunk

router = APIRouter()

@router.get("/status")
async def status():
    # DB checks
    db_ok = True
    db_error = None
    docs = chunks = None
    try:
        with SessionLocal() as s:
            s.execute(text("SELECT 1"))
            docs = s.query(Document).count()
            chunks = s.query(Chunk).count()
    except Exception as e:
        db_ok = False
        db_error = str(e)

    # Ollama checks
    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    ollama_ok = True
    ollama_error = None
    models = None
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(f"{ollama_base}/api/tags")
            r.raise_for_status()
            models = [m.get("name") for m in (r.json().get("models") or [])]
    except Exception as e:
        ollama_ok = False
        ollama_error = str(e)

    return {
        "ok": db_ok and ollama_ok,
        "db": {"ok": db_ok, "error": db_error, "documents": docs, "chunks": chunks},
        "ollama": {"ok": ollama_ok, "error": ollama_error, "base_url": ollama_base, "models": models},
    }
