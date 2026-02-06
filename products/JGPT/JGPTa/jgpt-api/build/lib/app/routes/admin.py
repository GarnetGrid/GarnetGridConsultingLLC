from __future__ import annotations
import os
# Admin routes for system configuration and maintenance.
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db.models import Chunk, Document, Image, Message, Conversation
from sqlalchemy import delete

router = APIRouter()

class SystemSettings(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    rerank: int | None = None
    vision_model: str | None = None

@router.get("/settings")
def get_settings():
    """Returns current editable system settings."""
    return {
        "chunk_size": int(os.getenv("CHUNK_SIZE", "300")),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "100")),
        "rerank": int(os.getenv("RERANK", "0")),
        "vision_model": os.getenv("VISION_MODEL", "llava:7b"),
        "embed_model": os.getenv("OLLAMA_EMBED_MODEL", "mxbai-embed-large"),
        "chat_model": os.getenv("CHAT_MODEL", "llama3.2")
    }

@router.post("/maintenance/clear-db")
async def clear_database():
    """Wipes all documents, chunks, images, and conversations from the database."""
    try:
        with SessionLocal() as s:
            s.execute(delete(Image))
            s.execute(delete(Chunk))
            s.execute(delete(Document))
            s.execute(delete(Message))
            s.execute(delete(Conversation))
            s.commit()
        return {"ok": True, "message": "Database cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.patch("/settings")
def update_settings(settings: SystemSettings):
    """Updates editable system settings for the current session."""
    if settings.chunk_size is not None:
        os.environ["CHUNK_SIZE"] = str(settings.chunk_size)
    if settings.chunk_overlap is not None:
        os.environ["CHUNK_OVERLAP"] = str(settings.chunk_overlap)
    if settings.rerank is not None:
        os.environ["RERANK"] = str(settings.rerank)
    if settings.vision_model is not None:
        os.environ["VISION_MODEL"] = settings.vision_model
    
    return {"ok": True, "settings": get_settings()}
