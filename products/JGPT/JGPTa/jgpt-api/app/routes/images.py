"""
Image-related API endpoints.
"""
from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.db.session import SessionLocal
from app.rag.image_retrieval import search_images, get_image_by_id, get_images_for_chunks


router = APIRouter(prefix="/images", tags=["images"])

STORAGE_ROOT = Path(__file__).resolve().parents[1] / "storage"


class ImageSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    min_similarity: float = 0.7


class ImageSearchResponse(BaseModel):
    images: list[dict]


@router.post("/search", response_model=ImageSearchResponse)
async def search_images_endpoint(req: ImageSearchRequest):
    """
    Search for images using semantic similarity on their descriptions.
    """
    with SessionLocal() as session:
        images = await search_images(
            query=req.query,
            session=session,
            top_k=req.top_k,
            min_similarity=req.min_similarity
        )
    
    return ImageSearchResponse(images=images)


@router.get("/{image_id}")
async def get_image_metadata(image_id: int):
    """
    Get image metadata by ID.
    """
    with SessionLocal() as session:
        image = get_image_by_id(image_id, session)
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image


@router.get("/{image_id}/file")
async def serve_image(image_id: int):
    """
    Serve the actual image file.
    """
    with SessionLocal() as session:
        image = get_image_by_id(image_id, session)
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Construct full path
    file_path = STORAGE_ROOT / image["storage_path"]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found on disk")
    
    return FileResponse(
        path=str(file_path),
        media_type=image["mime_type"],
        filename=image["filename"]
    )


@router.get("/chunks/{chunk_id}")
async def get_chunk_images(chunk_id: int):
    """
    Get all images associated with a specific chunk.
    """
    with SessionLocal() as session:
        images = get_images_for_chunks([chunk_id], session)
    
    return {"images": images}
