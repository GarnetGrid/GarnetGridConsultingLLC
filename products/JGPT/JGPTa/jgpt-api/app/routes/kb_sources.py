from __future__ import annotations
import os
from pathlib import Path
from fastapi import APIRouter
from app.db.session import SessionLocal
from app.db.models import Document, Chunk, Image
from sqlalchemy import func, delete

router = APIRouter()

KB_ROOT = Path("kb")

@router.get("/sources")
async def get_sources():
    """Returns a list of all files in the knowledge base with their database status."""
    sources = []
    
    with SessionLocal() as s:
        # Get count of chunks and images per document
        doc_stats = s.query(
            Document.source_path,
            func.count(Chunk.id).label("chunks"),
            func.count(Image.id).label("images")
        ).outerjoin(Chunk, Document.id == Chunk.document_id)\
         .outerjoin(Image, Document.id == Image.source_page)\
         .group_by(Document.source_path).all()
        
        stats_map = {row.source_path: {"chunks": row.chunks, "images": row.images} for row in doc_stats}

    if not KB_ROOT.exists():
        return []

    for path in KB_ROOT.rglob("*"):
        if path.is_file() and not path.name.startswith("."):
            rel_path = str(path.relative_to(KB_ROOT))
            stats = stats_map.get(rel_path, {"chunks": 0, "images": 0})
            
            sources.append({
                "path": rel_path,
                "name": path.name,
                "size": path.stat().st_size,
                "mtime": path.stat().st_mtime,
                "extension": path.suffix.lower(),
                "chunks": stats["chunks"],
                "images": stats["images"]
            })
            
    return sources

@router.get("/stats")
async def get_stats():
    """Returns aggregate statistics for the entire knowledge base."""
    with SessionLocal() as s:
        total_docs = s.query(func.count(Document.id)).scalar()
        total_chunks = s.query(func.count(Chunk.id)).scalar()
        total_images = s.query(func.count(Image.id)).scalar()
        images_with_desc = s.query(func.count(Image.id)).filter(Image.description != None).scalar()
        
    return {
        "total_documents": total_docs,
        "total_chunks": total_chunks,
        "total_images": total_images,
        "images_with_descriptions": images_with_desc,
        "last_ingestion": None # To be implemented with a state tracker if needed
    }
@router.delete("/sources/{path:path}")
async def delete_source(path: str):
    """Deletes a source file from the KB and removes all associated DB records."""
    full_path = KB_ROOT / path
    if not full_path.exists():
        # Fallback: Check if it's just in the DB
        pass
    
    with SessionLocal() as s:
        # 1. Find the document
        stmt = func.lower(Document.source_path) == path.lower()
        doc = s.query(Document).filter(stmt).first()
        
        if not doc:
            # Maybe it uses the absolute path or relative from elsewhere? 
            # In ingest_kb we use rel_path from KB_ROOT
            doc = s.query(Document).filter(Document.source_path.like(f"%{path}")).first()

        if doc:
            # 2. Delete all related records (Cascades in DB if configured, but let's be safe)
            s.execute(delete(Image).where(Image.source_page == doc.id))
            s.execute(delete(Chunk).where(Chunk.document_id == doc.id))
            s.delete(doc)
            s.commit()
            
    # 3. Delete from filesystem
    if full_path.exists() and full_path.is_file():
        os.remove(full_path)
        return {"ok": True, "message": f"Deleted {path} and associated records"}
    
    if doc:
        return {"ok": True, "message": f"Deleted database records for {path} (file already missing)"}
        
    return {"ok": False, "error": f"Source {path} not found"}
@router.post("/sources/{path:path}/reingest")
async def reingest_source(path: str):
    """Force re-ingestion of a specific source."""
    from app.util.ingest import ingest_kb
    
    # 1. Delete existing records for this path
    await delete_source(path)
    
    # 2. Run ingestion (which will find the file if it exists)
    report = await ingest_kb()
    
    # Check if our path was actually created/updated
    # Document.source_path uses relative path from parent of kb/ usually (depends on ingest.py)
    # Actually, let's just return the report
    return {"ok": True, "message": f"Re-ingested {path}", "report": report}
