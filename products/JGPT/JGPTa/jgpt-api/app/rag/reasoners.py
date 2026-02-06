from __future__ import annotations
import json
import os
from app.rag.ollama_client import ollama_chat

async def expand_query(query: str, domain: str = "general") -> list[str]:
    """Expands a user query into multiple technical search terms.
    Helps improve vector search hit rates.
    """
    model = os.getenv("CHAT_MODEL", "llama3.2")
    
    system = (
        "You are a search query optimizer. Expand the user query into 3-4 specific, "
        "technical search terms that would help find relevant information in a business "
        "knowledge base (Power BI, D365, etc.). "
        "Return STRICT JSON only: {\"queries\": [\"expanded 1\", \"expanded 2\"]}"
    )
    
    user_prompt = f"Domain: {domain}\nOriginal Query: {query}"
    
    try:
        content = await ollama_chat(model, system, user_prompt)
        # Attempt to find JSON if there's markdown fluff
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "{" in content:
            content = content[content.find("{"):content.rfind("}")+1]
            
        data = json.loads(content)
        queries = data.get("queries", [])
        # Include original query
        if query not in queries:
            queries.insert(0, query)
        return queries[:5]
    except Exception as e:
        print(f"Query Expansion failed: {e}")
        return [query]
