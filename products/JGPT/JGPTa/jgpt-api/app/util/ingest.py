from __future__ import annotations
import asyncio
import os
from pathlib import Path
from datetime import datetime

from sqlalchemy import select, delete
from app.db.session import SessionLocal
from app.db.models import Document, Chunk, Image, ChunkImage
from app.util.parsers import parse_file
from app.util.hashing import sha256_text
from app.util.image_processor import extract_images_from_pdf, extract_images_from_docx, save_image
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_one
from app.rag.vision_client import describe_image, check_vision_model_available
import logging

logger = logging.getLogger(__name__)

KB_ROOT = Path(__file__).resolve().parents[2] / "kb"
STORAGE_ROOT = Path(__file__).resolve().parents[2] / "storage" / "images"

def infer_domain(path: Path) -> str:
    parts = [p.lower() for p in path.parts]
    if "powerbi" in parts:
        return "powerbi"
    if "d365fo" in parts or "d365" in parts or "xpp" in parts:
        return "d365fo"
    return "general"

import re

def extract_metadata(text: str) -> dict:
    meta = {}
    # Look for **Key:** Value
    for match in re.finditer(r"\*\*(.*?):\*\*\s*(.*)", text):
        key = match.group(1).strip().lower()
        val = match.group(2).strip()
        meta[key] = val
    return meta

def infer_department(path: Path, meta: dict = None) -> str:
    # Check metadata first
    if meta and "department" in meta:
        return meta["department"].lower()

    parts = [p.lower() for p in path.parts]
    if "finance" in parts: return "finance"
    if "hr" in parts: return "hr"
    if "it" in parts or "ops" in parts: return "it"
    if "supply" in parts or "sc" in parts: return "supply"
    return "all"

async def ingest_kb() -> dict:
    if not KB_ROOT.exists():
        return {"ok": False, "error": f"KB root not found: {KB_ROOT}"}

    files = []
    for ext in ("*.md","*.markdown","*.pdf","*.docx", "*.txt", "*.csv"):
        files.extend(KB_ROOT.rglob(ext))
    files = sorted({f.resolve() for f in files})

    created = 0
    updated = 0
    skipped = 0
    images_processed = 0

    chunk_size = int(os.getenv("CHUNK_SIZE", "300"))
    overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
    logger.info(f"Using CHUNK_SIZE={chunk_size}, overlap={overlap}")
    
    # Check if vision model is available
    vision_available = await check_vision_model_available()
    if vision_available:
        logger.info("✓ Vision model available for image processing")
    else:
        logger.warning("⚠ Vision model not available - images will be stored without descriptions")

    for fp in files:
        rel = str(fp.relative_to(KB_ROOT.parent))
        text, mime = parse_file(fp)
        text = (text or "").strip()
        if not text:
            skipped += 1
            continue
        h = sha256_text(text)

        with SessionLocal() as s:
            existing = s.execute(select(Document).where(Document.source_path==rel)).scalar_one_or_none()
            if existing and existing.content_hash == h:
                skipped += 1
                continue

        meta = extract_metadata(text)
        domain = infer_domain(fp)
        dept = infer_department(fp, meta)
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

        # Extract images from document
        images = []
        if mime == "application/pdf":
            try:
                images = extract_images_from_pdf(fp)
            except Exception as e:
                logger.error(f"Failed to extract images from {fp}: {e}")
        elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                images = extract_images_from_docx(fp)
            except Exception as e:
                logger.error(f"Failed to extract images from {fp}: {e}")

        # embed + write
        with SessionLocal() as s:
            if existing:
                existing.domain = domain
                existing.department = dept
                existing.mime_type = mime
                existing.content_hash = h
                existing.content = text
                existing.updated_at = datetime.utcnow()
                s.execute(delete(Chunk).where(Chunk.document_id==existing.id))
                doc_id = existing.id
                updated += 1
            else:
                doc = Document(domain=domain, department=dept, source_path=rel, mime_type=mime, content_hash=h, content=text)
                s.add(doc); s.commit(); s.refresh(doc)
                doc_id = doc.id
                created += 1

            s.commit()

        # embed chunks outside the transaction loop for clarity (but still sequential)
        # embed chunks in parallel
        embeddings = await asyncio.gather(*[embed_one(ch) for ch in chunks])
        
        with SessionLocal() as s:
            first_chunk = None
            for i, (ch, emb) in enumerate(zip(chunks, embeddings)):
                chunk_obj = Chunk(document_id=doc_id, chunk_index=i, text=ch, embedding=emb)
                s.add(chunk_obj)
                if i == 0:
                     first_chunk = chunk_obj
            
            s.commit()
            
            # Image processing (associate with first chunk for now if needed, or just save images)
            if images and first_chunk:
                s.refresh(first_chunk)
                for img_data in images:
                    try:
                        # Save image to storage
                        img_path = save_image(img_data, STORAGE_ROOT)
                        
                        # Generate description
                        description = None
                        embedding = None
                        if vision_available:
                            try:
                                logger.info(f"  [vision] Describing {img_data.filename}...")
                                description = await describe_image(img_path)
                                if description:
                                    logger.info(f"  [vision] Generated {len(description)} chars of description")
                                    embedding = await embed_one(description)
                            except Exception as e:
                                logger.error(f"Failed to generate description for {img_path}: {e}")
                        
                        img_obj = Image(
                            filename=img_data.filename,
                            storage_path=str(img_path.relative_to(STORAGE_ROOT.parent)),
                            mime_type=img_data.mime_type,
                            width=img_data.width,
                            height=img_data.height,
                            description=description,
                            embedding=embedding,
                            source_page=img_data.source_page
                        )
                        s.add(img_obj)
                        s.commit()
                        s.refresh(img_obj)
                        
                        # Link to first chunk
                        chunk_img = ChunkImage(chunk_id=first_chunk.id, image_id=img_obj.id)
                        s.add(chunk_img)
                        s.commit()
                        
                        images_processed += 1
                    except Exception as e:
                        logger.error(f"Failed to process image {img_data.filename}: {e}")

    return {
        "ok": True, 
        "kb_root": str(KB_ROOT), 
        "created": created, 
        "updated": updated, 
        "skipped": skipped, 
        "total": len(files),
        "images_processed": images_processed
    }
