from __future__ import annotations
import json
from typing import Dict, Any
from app.db.session import SessionLocal
from app.rag.embeddings import embed_one
from app.rag.retriever import retrieve

def run(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Tool that allows the agent to search the Knowledge Base again with a new query."""
    query = inp.get("query")
    domain = inp.get("domain") or "all"
    department = inp.get("department")
    
    if not query:
        return {"ok": False, "error": "Missing 'query' input"}

    try:
        # Note: We need to run the async embed_one in a synchronous wrapper or 
        # use a separate sync version. Since this is called from wait_for, 
        # we'll use a trick or just assume we have it.
        # For simplicity in this tool, let's assume we can block or use a sync wrapper.
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        q_emb = loop.run_until_complete(embed_one(query))
        
        with SessionLocal() as s:
            citations, context_block, meta = loop.run_until_complete(
                retrieve(
                    s, query_text=query, query_emb=q_emb,
                    top_k=5, 
                    domain=domain if domain != "all" else None, 
                    mmr_lambda=0.7,
                    department=department
                )
            )
            loop.close()
            
        return {
            "ok": True,
            "results": context_block,
            "citations": [{"source": c["source"], "title": c["title"]} for c in citations]
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
