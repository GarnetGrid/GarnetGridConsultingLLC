from __future__ import annotations
from typing import Dict, Any
from app.db.session import SessionLocal
from app.rag.embeddings import embed_one
from app.rag.retriever import retrieve

async def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Tool that allows the agent to search the Knowledge Base again with a new query."""
    query = inp.get("query")
    domain = inp.get("domain") or "all"
    department = inp.get("department")
    
    if not query:
        return {"ok": False, "error": "Missing 'query' input"}

    try:
        q_emb = await embed_one(query)
        
        # Create a session for this retrieval operation
        # retrieve() is async but uses run_in_threadpool for blocking calls
        with SessionLocal() as s:
            citations, context_block, meta = await retrieve(
                s, query_text=query, query_emb=q_emb,
                top_k=5, 
                domain=domain if domain != "all" else None, 
                mmr_lambda=0.7,
                department=department
            )
            
        return {
            "ok": True,
            "results": context_block,
            "citations": [{"source": c["source"], "title": c["title"]} for c in citations]
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
