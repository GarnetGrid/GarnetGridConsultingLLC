from __future__ import annotations
from typing import List, Dict
import math

def dot(a: List[float], b: List[float]) -> float:
    return sum(x*y for x,y in zip(a,b))

def norm(a: List[float]) -> float:
    return math.sqrt(sum(x*x for x in a))

def cosine_sim(a: List[float], b: List[float]) -> float:
    na = norm(a); nb = norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot(a,b) / (na*nb)

def mmr_select(
    query_emb: List[float],
    candidates: List[Dict],
    k: int,
    lam: float = 0.7
) -> List[Dict]:
    """candidates: each dict must have keys: 'embedding' (list[float]) and metadata."""
    if not candidates:
        return []
    selected = []
    remaining = candidates[:]
    # precompute relevance
    for c in remaining:
        c["_rel"] = cosine_sim(query_emb, c["embedding"])
    # pick first best relevance
    remaining.sort(key=lambda x: x["_rel"], reverse=True)
    selected.append(remaining.pop(0))
    while remaining and len(selected) < k:
        best = None
        best_score = -1e9
        for c in remaining:
            diversity = max(cosine_sim(c["embedding"], s["embedding"]) for s in selected)
            score = lam * c["_rel"] - (1 - lam) * diversity
            if score > best_score:
                best_score = score
                best = c
        selected.append(best)
        remaining.remove(best)
    for s in selected:
        s.pop("_rel", None)
    return selected
