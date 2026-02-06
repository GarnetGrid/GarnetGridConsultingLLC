from __future__ import annotations
import asyncio

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import delete, select

from app.db.models import User
from app.util.auth import get_current_admin

from app.db.init_db import init_db
from app.db.models import Chunk, Document
from app.db.session import SessionLocal
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_one
from app.services.web_ingest import run_ingest
from app.util.ingest import ingest_kb, sha256_text
from app.util.url_ingest import scrape_url
from app.util.crawler import WebCrawler
from app.util.parsers import parse_text # reusing simple text parser logic or we just process raw HTML in ingest pipeline

router = APIRouter()

@router.post("/kb")
async def ingest_repo_kb(current_user: User = Depends(get_current_admin)):
    report = await ingest_kb()
    return report


@router.post("/web")
async def ingest_from_web(force: bool = False, max_pages: int = 0, current_user: User = Depends(get_current_admin)):
    """Fetch curated web sources into kb/web then ingest into vector store."""
    try:
        # Instead of running inline, we enqueue a job/jobs.
        # But 'web ingest' usually implies fetching multiple pages. 
        # For now, let's just trigger the background worker or enqueue if we had a job type for 'batch_crawl'.
        # Since we just added IngestionJob for single source, let's adapt or just run async for now.
        # Plan says "Refactor ingest.py into background worker loop".
        # So we should create a job.
        
        # NOTE: For 'batch' web ingest (curated list), we might need a 'BatchIngestionJob' or just spawn multiple jobs.
        # Let's spawn a job for 'full_ingest' special type or similar.
        with SessionLocal() as db:
             job = IngestionJob(
                 client_id="default", # TODO: get from user/token
                 status="pending",
                 source_type="system", # system command
                 source_target="web_ingest",
                 created_at=datetime.now(timezone.utc)
             )
             db.add(job)
             db.commit()
             db.refresh(job)
             
        return {"ok": True, "job_id": job.id, "status": "queued"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@router.post("/url")
async def ingest_single_url(url: str, current_user: User = Depends(get_current_admin)):
    """Scrape a single URL, chunk it, and index it into the vector store."""
    try:
        text = await scrape_url(url)
        # We can still scrape inline to validate, OR enqueue the scrape.
        # If we enqueue, we return immediately.
        # Plan: "enqueue jobs".
        
        with SessionLocal() as db:
             job = IngestionJob(
                 client_id="default",
                 status="pending",
                 source_type="url",
                 source_target=url,
                 created_at=datetime.now(timezone.utc)
             )
             db.add(job)
             db.commit()
             
        return {"ok": True, "status": "queued", "url": url}
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
        
    # Old inline logic removed in favor of queued job.

