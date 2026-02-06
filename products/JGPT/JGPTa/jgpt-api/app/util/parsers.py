from __future__ import annotations

from pathlib import Path
from typing import Tuple

from pypdf import PdfReader
import docx

def parse_markdown(path: Path) -> Tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text, "text/markdown"

def parse_pdf(path: Path) -> Tuple[str, str]:
    # 1. Try Azure Document Intelligence (Phase 10)
    try:
        from app.util.parsers_azure import is_azure_configured, parse_pdf_azure
        if is_azure_configured():
            try:
                print(f"pdf_ingest: using azure ocrid for {path.name}")
                return parse_pdf_azure(path)
            except Exception as e:
                print(f"pdf_ingest: azure failed, falling back to pypdf. error={e}")
    except ImportError:
        pass

    # 2. Try Local Hybrid OCR (Phase 10 Alternative)
    try:
        from app.util.parsers_local import parse_pdf_local
        print(f"pdf_ingest: using local hybrid parser for {path.name}")
        return parse_pdf_local(path)
    except ImportError as e:
        print(f"pdf_ingest: local parser import failed ({e}), falling back to pypdf")

    # 3. Fallback to basic pypdf (Legacy)
    print(f"pdf_ingest: using primitive pypdf for {path.name}")
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append((page.extract_text() or "").strip())
    return "\n\n".join([p for p in parts if p]), "application/pdf"

def parse_docx(path: Path) -> Tuple[str, str]:
    d = docx.Document(str(path))
    parts = []
    for p in d.paragraphs:
        t = (p.text or "").strip()
        if t:
            parts.append(t)
    return "\n".join(parts), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

def parse_text(path: Path) -> Tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text, "text/plain"

def parse_file(path: Path) -> Tuple[str, str]:
    ext = path.suffix.lower()
    if ext in [".md", ".markdown"]:
        return parse_markdown(path)
    if ext == ".pdf":
        return parse_pdf(path)
    if ext == ".docx":
        return parse_docx(path)
    if ext in [".txt", ".csv"]:
        return parse_text(path)
    raise ValueError(f"Unsupported file type: {ext}")
