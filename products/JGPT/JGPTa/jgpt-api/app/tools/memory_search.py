from typing import Dict, Any, List
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import Message
from app.rag.embeddings import embed_one
import asyncio
from app.services.context_service import ContextService 

async def search_history(inp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Searches your own conversation history (long-term memory) for past discussions.
    Use this when the user refers to "last time" or "what we discussed about X".
    
    Args:
        query: The semantic search query (e.g. "project falcon details", "my previous python script").
        limit: Number of results to return (default 5).
    """
    query = inp.get("query")
    limit = inp.get("limit", 5)
    
    if not query:
        return {"ok": False, "error": "query is required"}
        
    try:
        # 1. Embed query (Async)
        q_emb = await embed_one(query)
        
        # 2. Search DB (Sync wrapper)
        def _search_db(emb, k):
            with SessionLocal() as db:
                # pgvector cosine distance definition: messages.embedding.l2_distance(emb) or cosine_distance
                # SQLAlchemy pgvector: Message.embedding.cosine_distance(emb)
                stmt = select(Message).order_by(Message.embedding.cosine_distance(emb)).limit(k)
                results = db.scalars(stmt).all()
                
                out = []
                for msg in results:
                    # Basic metadata
                    preview = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                    out.append({
                        "id": msg.id,
                        "role": msg.role,
                        "content": preview,
                        "date": str(msg.created_at)
                    })
                return out

        # Since this tool might be called from async context (api loop), need to run sync DB op carefully?
        # The tool selector runs `await fn(t_input)` if it is coroutine.
        # But `_search_db` is sync. We can just call it if we accept blocking, or define this tool as async.
        # This file defines `search_history` as `async def`, so we are good.
        
        # Wait, if we use SessionLocal inside async def without run_in_threadpool, we block loop.
        # We should use run_in_threadpool or just accept it if fast.
        # Let's use run_in_threadpool from fastapi.concurrency
        from fastapi.concurrency import run_in_threadpool
        
        hits = await run_in_threadpool(_search_db, q_emb, limit)
        
        return {"ok": True, "results": hits}
        
    except Exception as e:
        return {"ok": False, "error": f"Search failed: {str(e)}"}
