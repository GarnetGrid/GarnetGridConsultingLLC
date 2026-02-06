from __future__ import annotations

import os
from typing import List

from app.rag.ollama_client import ollama_embed

# Embedding provider selection
# - EMBED_PROVIDER=ollama uses Ollama /api/embeddings
# - otherwise, fall back to the existing local/default provider (if any)
EMBED_PROVIDER = os.getenv("EMBED_PROVIDER", "ollama").lower().strip()
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", os.getenv("EMBED_MODEL", "mxbai-embed-large"))

async def embed_one(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return [0.0] * 1024  # fallback; should not happen normally

    if EMBED_PROVIDER == "ollama":
        return await ollama_embed(OLLAMA_EMBED_MODEL, text)

    # If you later add other providers, implement here.
    # For now default to Ollama to keep the stack fully local/offline.
    return await ollama_embed(OLLAMA_EMBED_MODEL, text)
