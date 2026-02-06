from __future__ import annotations
import asyncio
import os
from pathlib import Path
from datetime import datetime
import logging
from sqlalchemy import select, delete
from app.db.session import SessionLocal
from app.db.models import Document, Chunk, Image, ChunkImage
from app.util.parsers import parse_file
from app.util.hashing import sha256_text
from app.util.image_processor import extract_images_from_pdf, extract_images_from_docx, save_image
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_one
from app.rag.vision_client import describe_image, check_vision_model_available

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, kb_root: Path = None, storage_root: Path = None):
        if not kb_root:
            kb_root = Path(__file__).resolve().parents[2] / "kb"
        if not storage_root:
             storage_root = Path(__file__).resolve().parents[2] / "storage" / "images"
        
        self.kb_root = kb_root
        self.storage_root = storage_root
        
    def infer_domain(self, path: Path) -> str:
        parts = [p.lower() for p in path.parts]
        if "powerbi" in parts: return "powerbi"
        if "d365fo" in parts or "d365" in parts or "xpp" in parts: return "d365fo"
        return "general"

    def extract_metadata(self, text: str) -> dict:
        import re
        meta = {}
        for match in re.finditer(r"\*\*(.*?):\*\*\s*(.*)", text):
            key = match.group(1).strip().lower()
            val = match.group(2).strip()
            meta[key] = val
        return meta
    
    def infer_department(self, path: Path, meta: dict = None) -> str:
        if meta and "department" in meta: return meta["department"].lower()
        parts = [p.lower() for p in path.parts]
        if "finance" in parts: return "finance"
        if "hr" in parts: return "hr"
        if "it" in parts or "ops" in parts: return "it"
        if "supply" in parts or "sc" in parts: return "supply"
        return "all"

    async def run_ingestion(self) -> dict:
        if not self.kb_root.exists():
            return {"ok": False, "error": f"KB root not found: {self.kb_root}"}

        files = []
        for ext in ("*.md", "*.markdown", "*.pdf", "*.docx", "*.txt", "*.csv"):
            files.extend(self.kb_root.rglob(ext))
        files = sorted({f.resolve() for f in files})
        
        stats = {"created": 0, "updated": 0, "skipped": 0, "images_processed": 0}
        chunk_size = int(os.getenv("CHUNK_SIZE", "300"))
        overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
        
        vision_available = await check_vision_model_available()
        
        for fp in files:
             await self._process_file(fp, chunk_size, overlap, vision_available, stats)
             
        stats["ok"] = True
        stats["total"] = len(files)
        return stats

    async def _process_file(self, fp: Path, chunk_size: int, overlap: int, vision_available: bool, stats: dict):
        try:
            rel = str(fp.relative_to(self.kb_root.parent))
            text, mime = parse_file(fp)
            text = (text or "").strip()
            
            if not text:
                stats["skipped"] += 1
                return
            
            h = sha256_text(text)
            
            # Check existing
            doc_id = None
            is_update = False
            
            with SessionLocal() as s:
                existing = s.execute(select(Document).where(Document.source_path==rel)).scalar_one_or_none()
                if existing and existing.content_hash == h:
                    stats["skipped"] += 1
                    return
                
                meta = self.extract_metadata(text)
                domain = self.infer_domain(fp)
                dept = self.infer_department(fp, meta)
                
                if existing:
                    existing.domain = domain
                    existing.department = dept
                    existing.mime_type = mime
                    existing.content_hash = h
                    existing.content = text
                    existing.updated_at = datetime.utcnow()
                    # Clear old chunks
                    s.execute(delete(Chunk).where(Chunk.document_id==existing.id))
                    doc_id = existing.id
                    is_update = True
                    stats["updated"] += 1
                else:
                    doc = Document(domain=domain, department=dept, source_path=rel, mime_type=mime, content_hash=h, content=text)
                    s.add(doc); s.commit(); s.refresh(doc)
                    doc_id = doc.id
                    stats["created"] += 1
                s.commit()
            
            # Chunking and Embedding
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            embeddings = await asyncio.gather(*[embed_one(ch) for ch in chunks])
            
            with SessionLocal() as s:
                first_chunk_obj = None
                for i, (ch, emb) in enumerate(zip(chunks, embeddings)):
                    chunk_obj = Chunk(document_id=doc_id, chunk_index=i, text=ch, embedding=emb)
                    s.add(chunk_obj)
                    if i == 0: first_chunk_obj = chunk_obj
                s.commit()
                
                # Image processing
                if first_chunk_obj:
                    await self._process_images(fp, mime, first_chunk_obj, vision_available, s, stats)
                    
        except Exception as e:
            logger.error(f"Error processing {fp}: {e}")

    async def _process_images(self, fp: Path, mime: str, first_chunk, vision_available: bool, session, stats: dict):
        images = []
        if mime == "application/pdf":
             try: images = extract_images_from_pdf(fp)
             except: pass
        elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
             try: images = extract_images_from_docx(fp)
             except: pass
             
        if not images: return
        
        session.refresh(first_chunk)
        for img_data in images:
            try:
                img_path = save_image(img_data, self.storage_root)
                desc = None
                emb = None
                
                if vision_available:
                    desc = await describe_image(img_path)
                    if desc: emb = await embed_one(desc)
                    
                img_obj = Image(
                    filename=img_data.filename,
                    storage_path=str(img_path.relative_to(self.storage_root.parent)),
                    mime_type=img_data.mime_type,
                    width=img_data.width,
                    height=img_data.height,
                    description=desc,
                    embedding=emb,
                    source_page=img_data.source_page
                )
                session.add(img_obj)
                session.commit()
                session.refresh(img_obj)
                
                chunk_img = ChunkImage(chunk_id=first_chunk.id, image_id=img_obj.id)
                session.add(chunk_img)
                session.commit()
                stats["images_processed"] += 1
            except Exception as e:
                logger.error(f"Image error {fp}: {e}")

# Global instance
ingestion_service = IngestionService()
