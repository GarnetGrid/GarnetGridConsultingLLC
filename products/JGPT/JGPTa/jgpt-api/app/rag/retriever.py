from __future__ import annotations

import time
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.rag.mmr import mmr_select
from app.rag.reranker import rerank
from app.rag.image_retrieval import get_images_for_chunks

from fastapi.concurrency import run_in_threadpool

def _fetch_candidates_sync(session: Session, query_text: str, query_emb: list[float], pool_size: int, domain: str | None, department: str | list[str] | None):
    # 1. Vector Search
    vec_stmt = (
        select(
            Chunk.id,
            Chunk.text,
            Chunk.embedding,
            Document.source_path,
            Document.domain,
        )
        .join(Document, Document.id == Chunk.document_id)
    )
    if domain and domain != "all":
        vec_stmt = vec_stmt.where(Document.domain == domain)
    if department and department != "all":
        if isinstance(department, list):
             vec_stmt = vec_stmt.where(Document.department.in_(department))
        else:
             vec_stmt = vec_stmt.where(Document.department == department)
    
    vec_stmt = vec_stmt.order_by(Chunk.embedding.cosine_distance(query_emb)).limit(pool_size)
    vec_rows = session.execute(vec_stmt).all()

    # 2. Full-Text Search (FTS)
    from sqlalchemy import func
    fts_rows = []
    
    fts_stmt = (
        select(
            Chunk.id,
            Chunk.text,
            Chunk.embedding,
            Document.source_path,
            Document.domain,
        )
        .join(Document, Document.id == Chunk.document_id)
    )
    if domain and domain != "all":
        fts_stmt = fts_stmt.where(Document.domain == domain)
    if department and department != "all":
        if isinstance(department, list):
             fts_stmt = fts_stmt.where(Document.department.in_(department))
        else:
             fts_stmt = fts_stmt.where(Document.department == department)
    
    fts_stmt = fts_stmt.where(Chunk.tsv.op("@@")(func.plainto_tsquery('english', query_text)))
    fts_stmt = fts_stmt.order_by(func.ts_rank_cd(Chunk.tsv, func.plainto_tsquery('english', query_text)).desc()).limit(pool_size)
    
    try:
        fts_rows = session.execute(fts_stmt).all()
    except Exception as e:
        print(f"FTS Search failed: {e}")
        fts_rows = []

    # 3. Reciprocal Rank Fusion (RRF)
    K = 60
    scores = {} # cid -> score
    data = {}   # cid -> row_dict
    
    # Collect Vector Ranks
    for i, r in enumerate(vec_rows):
        cid = int(r.id)
        scores[cid] = scores.get(cid, 0) + 1.0 / (K + i + 1)
        data[cid] = {
            "chunk_id": cid,
            "text": str(r.text),
            "embedding": list(r.embedding),
            "source": str(r.source_path),
            "domain": str(r.domain),
            "rank_source": "vector"
        }
        
    # Collect FTS Ranks
    for i, r in enumerate(fts_rows):
        cid = int(r.id)
        scores[cid] = scores.get(cid, 0) + 1.0 / (K + i + 1)
        if cid not in data:
            data[cid] = {
                "chunk_id": cid,
                "text": str(r.text),
                "embedding": list(r.embedding),
                "source": str(r.source_path),
                "domain": str(r.domain),
                "rank_source": "fts"
            }
        else:
            data[cid]["rank_source"] = "hybrid"

    # Sort by RRF score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    merged = [data[cid] for cid in sorted_ids]
    return merged, len(fts_rows)

async def retrieve(session: Session, query_text: str, query_emb: list[float], top_k: int, domain: str | None, mmr_lambda: float, department: str | list[str] | None = None):
    t0 = time.perf_counter()
    pool_size = max(top_k * 6, 40)

    # 1. DB Fetch (Blocking -> Threadpool)
    merged, fts_count = await run_in_threadpool(
        _fetch_candidates_sync, 
        session=session, 
        query_text=query_text, 
        query_emb=query_emb, 
        pool_size=pool_size, 
        domain=domain, 
        department=department
    )

    # 2. MMR (CPU Bound - fast enough for <100 items, keeping in main thread for simplicity)
    mmr_selected = mmr_select(query_emb, merged, k=min(top_k*3, len(merged)), lam=mmr_lambda)

    # 3. Rerank (Async HTTP)
    selected = await rerank(query_text, mmr_selected, top_k=top_k)
    
    # 4. Image Fetch (Blocking -> Threadpool)
    chunk_ids = [s["chunk_id"] for s in selected]
    images = []
    if chunk_ids:
        images = await run_in_threadpool(get_images_for_chunks, chunk_ids, session)

    citations = []
    context_lines = []
    for s in selected:
        text = s.get("text") or ""
        title = ""
        for ln in text.splitlines():
            if ln.strip().startswith("#"):
                title = ln.lstrip("#").strip()
                break
        snippet = text[:700].replace("\n"," ").strip()
        
        # Find images for this chunk and inject descriptions into context
        chunk_images = [img for img in images if int(img.get("chunk_id") or 0) == int(s["chunk_id"]) ]
        
        image_context = ""
        for img in chunk_images:
            if img.get("description"):
                image_context += f"\n[IMAGE DESCRIPTION ({img['filename']}): {img['description']}]"

        citations.append({
            "chunk_id": s["chunk_id"],
            "source": s["source"],
            "domain": s["domain"],
            "title": title,
            "snippet": snippet,
            "text": text,
            "rank_type": s.get("rank_source", "vector"),
            "images": chunk_images  # Include images in citation
        })
        
        context_body = (f"{title}: " if title else "") + snippet + image_context
        context_lines.append(f"- ({s['source']} :: chunk {s['chunk_id']}) {context_body}")

    t1 = time.perf_counter()
    meta = {
        "pool": pool_size,
        "hybrid_count": len(merged),
        "keyword_hits": fts_count,
        "selected": len(selected),
        "mmr_lambda": mmr_lambda,
        "rerank": True,
        "ms": int((t1 - t0) * 1000),
        "images_found": len(images)
    }
    return citations, "\n".join(context_lines), meta
