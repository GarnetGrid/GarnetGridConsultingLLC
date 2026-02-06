from __future__ import annotations

import re

HEADER_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

def _split_markdown_blocks(text: str) -> list[str]:
    """Split markdown into blocks by headings while keeping fenced code blocks intact."""
    text = (text or "").replace("\r\n", "\n")
    if not text.strip():
        return []

    blocks: list[str] = []
    buf: list[str] = []
    in_code = False

    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            buf.append(line)
            continue

        if (not in_code) and HEADER_RE.match(line):
            if buf:
                blocks.append("\n".join(buf).strip())
                buf = []
        buf.append(line)

    if buf:
        blocks.append("\n".join(buf).strip())

    return [b for b in blocks if b]

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Production-grade chunker:
    - Extracts context from document headers.
    - Uses sliding window with overlap for large blocks.
    - Prepend context to each chunk to enhance retrieval recall.
    """
    if not text.strip():
        return []

    # 1. Extract Main Title (Context)
    main_title = ""
    lines = text.splitlines()
    for line in lines[:20]:
        if line.strip().startswith("# "):
            main_title = line.strip().lstrip("#").strip()
            break
    
    # 2. Split into blocks by headers
    blocks = _split_markdown_blocks(text)
    
    chunks: list[str] = []
    
    for block in blocks:
        # Determine current block context (first heading in block if any)
        heading_match = HEADER_RE.search(block)
        current_heading = heading_match.group(2).strip() if heading_match else ""
        
        context_prefix = ""
        if main_title:
            context_prefix = f"[Document: {main_title}] "
        if current_heading and current_heading != main_title:
            context_prefix += f"[Section: {current_heading}] "
            
        # If block + prefix fits in chunk_size, keep it together
        if len(context_prefix) + len(block) <= chunk_size:
            chunks.append(context_prefix + block)
        else:
            # Sliding window for large blocks
            effective_chunk_size = chunk_size - len(context_prefix)
            if effective_chunk_size <= 0: # Sanity check for massive headers
                effective_chunk_size = chunk_size // 2
                
            start = 0
            while start < len(block):
                end = start + effective_chunk_size
                chunk_slice = block[start:end]
                chunks.append(context_prefix + chunk_slice)
                start = end - overlap
                if start >= len(block) - overlap: # Avoid tiny tails
                    break
                    
    return chunks
