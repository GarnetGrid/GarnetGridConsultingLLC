
import logging
from pathlib import Path
from typing import Tuple, List

# External libs (installed via pip)
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def is_ocr_available() -> bool:
    """
    Checks if Tesseract and Poppler are available.
    """
    try:
        # Check Tesseract
        pytesseract.get_tesseract_version()
        # Poppler check is implicitly done when calling convert_from_path, 
        # but hard to check without actually running it or checking shutil.which
        import shutil
        if not shutil.which("pdftoppm") and not shutil.which("pdftocairo"):
             return False
        return True
    except Exception:
        return False

def parse_pdf_local(path: Path) -> Tuple[str, str]:
    """
    Hybrid PDF Parser:
    1. Extracts native text.
    2. If text is sparse (< 50 chars), runs OCR on the page.
    """
    try:
        reader = PdfReader(str(path))
    except Exception as e:
        logger.error(f"Failed to read PDF {path}: {e}")
        return "", "application/pdf"
        
    final_text = []
    
    # Check if we should even try OCR (expensive)
    # If the user hasn't installed tools, fallback to just text
    ocr_ready = is_ocr_available()
    
    # We might need to render pages if we decide to OCR
    # Loading all images at once can be heavy, so we might do it page-by-page or lazy
    # But pdf2image converts whole PDF usually. 
    # For efficiency, we only convert IF we detect sparse text.
    
    # Heuristic: Check density first
    # This might be slow if we have to re-open for pdf2image multiple times.
    # A simple approach: Iterate pages, check text.
    
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        
        # Heuristic: User slides often have LITTLE text (just a title) + big image
        # If text length < 100, we try OCR if available
        if len(text) < 100 and ocr_ready:
            try:
                logger.info(f"Page {i+1} has sparse text ({len(text)} chars). Attempting OCR.")
                # Convert specific page to image
                # poppler uses 1-based indexing for first_page/last_page
                images = convert_from_path(str(path), first_page=i+1, last_page=i+1)
                if images:
                    ocr_text = pytesseract.image_to_string(images[0])
                    # If OCR adds significant new text, append it
                    if len(ocr_text) > len(text):
                        text += f"\n\n[OCR Text]\n{ocr_text}"
            except Exception as e:
                logger.warning(f"OCR failed for page {i+1} of {path.name}: {e}")
        
        final_text.append(text)

    return "\n\n".join(final_text), "application/pdf"
