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
        # Phase 1: Fetch content (now async & parallel)
        fetch_report = await run_ingest(force=force, max_pages=max_pages)
        
        # Phase 2: Vector Ingest (only if fetch didn't critically fail)
        if fetch_report.get("ok"):
            kb_report = await ingest_kb()
            return {"ok": True, "fetch": fetch_report, "kb": kb_report}
        else:
            return JSONResponse(status_code=500, content={"ok": False, "fetch": fetch_report, "error": "web fetch failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@router.post("/url")
async def ingest_single_url(url: str, current_user: User = Depends(get_current_admin)):
    """Scrape a single URL, chunk it, and index it into the vector store."""
    try:
        text = await scrape_url(url)
        h = sha256_text(text)
        
        # Ingest into DB
        with SessionLocal() as s:
            # Check for existing
            stmt = select(Document).where(Document.source_path == url)
            existing = s.execute(stmt).scalar_one_or_none()
            
            if existing:
                if existing.content_hash == h:
                    return {"ok": True, "url": url, "chunks": 0, "status": "skipped"}
                # Update existing
                existing.content_hash = h
                existing.content = text
                existing.updated_at = datetime.now(timezone.utc)
                s.execute(delete(Chunk).where(Chunk.document_id == existing.id))
                doc_id = existing.id
            else:
                doc = Document(
                    source_path=url, 
                    domain="general", 
                    department="all", 
                    mime_type="text/html",
                    content_hash=h,
                    content=text
                )
                s.add(doc); s.commit(); s.refresh(doc)
                doc_id = doc.id
            
            # Use existing chunker
            chunks = chunk_text(text, chunk_size=1000, overlap=100)
            
            # Parallel embedding
            embeddings = await asyncio.gather(*[embed_one(c) for c in chunks])
            
            for i, (c, emb) in enumerate(zip(chunks, embeddings)):
                s.add(Chunk(document_id=doc_id, chunk_index=i, text=c, embedding=emb))
            s.commit()
            
        return {"ok": True, "url": url, "chunks": len(chunks)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

@router.post("/crawl")
async def crawl_site(
    url: str, 
    depth: int = 1, 
    max_pages: int = 10, 
    current_user: User = Depends(get_current_admin)
):
    """Crawl a website recursively and ingest found pages."""
    try:
        crawler = WebCrawler(start_url=url, max_depth=depth, max_pages=max_pages)
        results = await crawler.run()
        
        ingested_count = 0
        
        with SessionLocal() as s:
            for page in results:
                page_url = page['url']
                html = page['content']
                
                # Simple extraction for now (using existing utils if possible or soup)
                # We can reuse convert_to_markdown if imported, or just strip tags
                from app.util.url_ingest import convert_to_markdown
                text = convert_to_markdown(html)
                h = sha256_text(text)
                
                # Check for existing
                existing = s.execute(select(Document).where(Document.source_path == page_url)).scalar_one_or_none()
                if existing and existing.content_hash == h:
                    continue

                if existing:
                    existing.content = text
                    existing.content_hash = h
                    existing.updated_at = datetime.now(timezone.utc)
                    s.execute(delete(Chunk).where(Chunk.document_id == existing.id))
                    doc_id = existing.id
                else:
                    doc = Document(
                        source_path=page_url,
                        domain="web",
                        department="all",
                        mime_type="text/html",
                        content_hash=h,
                        content=text
                    )
                    s.add(doc); s.commit(); s.refresh(doc)
                    doc_id = doc.id
                
                # Chunking
                chunks = chunk_text(text, chunk_size=1000, overlap=100)
                embeddings = await asyncio.gather(*[embed_one(c) for c in chunks])
                
                for i, (c, emb) in enumerate(zip(chunks, embeddings)):
                    s.add(Chunk(document_id=doc_id, chunk_index=i, text=c, embedding=emb))
                
                ingested_count += 1
            s.commit()
            
        return {"ok": True, "base_url": url, "pages_found": len(results), "pages_ingested": ingested_count}

    except Exception as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
