"""
Image retrieval and search utilities.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models import Image, ChunkImage, Chunk
from app.rag.embeddings import embed_one


async def search_images(
    query: str,
    session: Session,
    top_k: int = 5,
    min_similarity: float = 0.7
) -> list[dict]:
    """
    Search for images using semantic similarity on their descriptions.
    
    Args:
        query: Search query
        session: Database session
        top_k: Number of results to return
        min_similarity: Minimum similarity threshold (0-1)
        
    Returns:
        List of image results with metadata
    """
    # Embed the query
    query_embedding = await embed_one(query)
    
    # Search for similar images using cosine similarity
    results = session.execute(
        select(
            Image,
            (1 - func.cosine_distance(Image.embedding, query_embedding)).label("similarity")
        )
        .where(Image.embedding.isnot(None))
        .order_by(func.cosine_distance(Image.embedding, query_embedding))
        .limit(top_k)
    ).all()
    
    # Filter by minimum similarity and format results
    images = []
    for img, similarity in results:
        if similarity >= min_similarity:
            images.append({
                "id": img.id,
                "filename": img.filename,
                "storage_path": img.storage_path,
                "description": img.description,
                "width": img.width,
                "height": img.height,
                "source_page": img.source_page,
                "source_url": img.source_url,
                "similarity": float(similarity)
            })
    
    return images


def get_images_for_chunks(chunk_ids: list[int], session: Session) -> list[dict]:
    """
    Get all images associated with a list of chunks.
    
    Args:
        chunk_ids: List of chunk IDs
        session: Database session
        
    Returns:
        List of image metadata
    """
    # Return mapping-aware rows so the caller can attach the right images to the right chunk.
    rows = session.execute(
        select(ChunkImage.chunk_id, Image)
        .join(Image, ChunkImage.image_id == Image.id)
        .where(ChunkImage.chunk_id.in_(chunk_ids))
    ).all()

    out: list[dict] = []
    for chunk_id, img in rows:
        out.append(
            {
                "chunk_id": int(chunk_id),
                "id": img.id,
                "filename": img.filename,
                "storage_path": img.storage_path,
                "description": img.description,
                "width": img.width,
                "height": img.height,
                "source_page": img.source_page,
                "source_url": img.source_url,
            }
        )
    return out


def get_image_by_id(image_id: int, session: Session) -> Optional[dict]:
    """
    Get image metadata by ID.
    
    Args:
        image_id: Image ID
        session: Database session
        
    Returns:
        Image metadata or None
    """
    img = session.execute(
        select(Image).where(Image.id == image_id)
    ).scalar_one_or_none()
    
    if not img:
        return None
    
    return {
        "id": img.id,
        "filename": img.filename,
        "storage_path": img.storage_path,
        "description": img.description,
        "width": img.width,
        "height": img.height,
        "source_page": img.source_page,
        "source_url": img.source_url,
        "mime_type": img.mime_type
    }
