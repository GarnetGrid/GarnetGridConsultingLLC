from __future__ import annotations

import os
import json
from typing import List, Dict, Any

from app.rag.ollama_client import ollama_chat

RERANK_ENABLED = os.getenv("RERANK", "0").lower().strip() in ("1","true","yes","on")
RERANK_MODEL = os.getenv("RERANK_MODEL", os.getenv("CHAT_MODEL", "llama3.2"))
RERANK_POOL = int(os.getenv("RERANK_POOL", "50"))

_SYSTEM = """You are a precision relevance scorer for a RAG system.
Evaluate the following candidate snippets based on the user query.
Assign a score from 0 to 100 where:
- 100: Evidence is perfect, directly answers the query with high confidence.
- 70-99: Evidence is very relevant and helpful, but might be missing small details.
- 40-69: Evidence is somewhat relevant or related to the topic but doesn't answer the query directly.
- 0-39: Evidence is irrelevant, a mismatch, or just generic noise.

Return ONLY a JSON object in this exact format:
{"scores": [{"i": int, "score": int}]}
"""

async def rerank(query: str, candidates: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    if not RERANK_ENABLED:
        return candidates[:top_k]

    pool = candidates[:max(top_k, min(len(candidates), RERANK_POOL))]

    items = []
    for i, c in enumerate(pool):
        items.append({
            "i": i,
            "source": c.get("source"),
            "chunk_id": c.get("chunk_id"),
            "text": (c.get("text") or "")[:800]
        })

    user = json.dumps({"query": query, "candidates": items}, ensure_ascii=False)

    out = await ollama_chat(RERANK_MODEL, _SYSTEM, user, timeout_s=120.0)
    # Expected: {"scores":[{"i":0,"score":87}, ...]}
    try:
        data = json.loads(out)
        scores = {int(s["i"]): float(s["score"]) for s in (data.get("scores") or []) if "i" in s and "score" in s}
    except Exception:
        # If reranker fails, fall back to original order
        return pool[:top_k]

    ranked = sorted(list(enumerate(pool)), key=lambda t: scores.get(t[0], 0.0), reverse=True)
    return [c for _, c in ranked[:top_k]]
