"""
Image processing utilities for extracting and handling images from documents.
"""
from __future__ import annotations

import io
import hashlib
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from PIL import Image
import httpx


@dataclass
class ImageData:
    """Container for image data and metadata"""
    content: bytes
    filename: str
    mime_type: str
    width: int
    height: int
    source_page: Optional[int] = None  # For PDFs
    source_url: Optional[str] = None


def extract_images_from_pdf(pdf_path: Path) -> list[ImageData]:
    """
    Extract images from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of ImageData objects
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF image extraction. Install with: pip install PyMuPDF")
    
    images = []
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Open with PIL to get dimensions
            pil_image = Image.open(io.BytesIO(image_bytes))
            width, height = pil_image.size
            
            # Skip very small images (likely icons or decorations)
            if width < 100 or height < 100:
                continue
            
            mime_type = f"image/{image_ext}"
            filename = f"{pdf_path.stem}_p{page_num + 1}_img{img_index + 1}.{image_ext}"
            
            images.append(ImageData(
                content=image_bytes,
                filename=filename,
                mime_type=mime_type,
                width=width,
                height=height,
                source_page=page_num + 1
            ))
    
    doc.close()
    return images


def extract_images_from_docx(docx_path: Path) -> list[ImageData]:
    """
    Extract images from a DOCX file.
    
    Args:
        docx_path: Path to the DOCX file
        
    Returns:
        List of ImageData objects
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required. Install with: pip install python-docx")
    
    images = []
    doc = Document(docx_path)
    
    # Extract images from document relationships
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_bytes = rel.target_part.blob
            
            # Determine mime type from content type
            content_type = rel.target_part.content_type
            ext = content_type.split('/')[-1]
            
            # Open with PIL to get dimensions
            pil_image = Image.open(io.BytesIO(image_bytes))
            width, height = pil_image.size
            
            # Skip very small images
            if width < 100 or height < 100:
                continue
            
            filename = f"{docx_path.stem}_img{len(images) + 1}.{ext}"
            
            images.append(ImageData(
                content=image_bytes,
                filename=filename,
                mime_type=content_type,
                width=width,
                height=height
            ))
    
    return images


async def download_image(url: str, timeout: float = 30.0) -> Optional[ImageData]:
    """
    Download an image from a URL.
    
    Args:
        url: Image URL
        timeout: Request timeout in seconds
        
    Returns:
        ImageData object or None if download fails
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            image_bytes = response.content
            content_type = response.headers.get("content-type", "image/jpeg")
            
            # Open with PIL to validate and get dimensions
            pil_image = Image.open(io.BytesIO(image_bytes))
            width, height = pil_image.size
            
            # Skip very small images
            if width < 100 or height < 100:
                return None
            
            # Extract filename from URL or generate one
            filename = url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                ext = content_type.split('/')[-1]
                filename = f"image_{hashlib.md5(url.encode()).hexdigest()[:8]}.{ext}"
            
            return ImageData(
                content=image_bytes,
                filename=filename,
                mime_type=content_type,
                width=width,
                height=height,
                source_url=url
            )
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None


def save_image(image_data: ImageData, storage_dir: Path) -> Path:
    """
    Save image to storage directory.
    
    Args:
        image_data: ImageData object
        storage_dir: Directory to save images
        
    Returns:
        Path to saved image file
    """
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename using hash if needed
    base_name = Path(image_data.filename).stem
    ext = Path(image_data.filename).suffix
    
    # Add hash to prevent collisions
    content_hash = hashlib.md5(image_data.content).hexdigest()[:8]
    unique_filename = f"{base_name}_{content_hash}{ext}"
    
    file_path = storage_dir / unique_filename
    file_path.write_bytes(image_data.content)
    
    return file_path


def resize_image_for_vision(image_path: Path, max_size: int = 1024) -> bytes:
    """
    Resize image for vision model processing.
    
    Args:
        image_path: Path to image file
        max_size: Maximum dimension (width or height)
        
    Returns:
        Resized image bytes
    """
    img = Image.open(image_path)
    
    # Calculate new dimensions maintaining aspect ratio
    width, height = img.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Convert to RGB if necessary
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    
    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()
