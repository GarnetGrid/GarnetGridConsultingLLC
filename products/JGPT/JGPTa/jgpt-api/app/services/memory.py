from __future__ import annotations
import os
from app.rag.ollama_client import ollama_chat

async def summarize_history(messages: list[dict], max_turns: int = 10) -> str:
    """Summarizes a long message history into a concise context block.
    Only takes effect if messages count exceeds max_turns.
    """
    if len(messages) <= max_turns:
        return ""

    model = os.getenv("CHAT_MODEL", "llama3.2")
    
    system = (
        "You are a conversation memory assistant. Summarize the preceding conversation "
        "into a single, concise paragraph. Focus on the core user intent, the entities "
        "being discussed (Power BI reports, D365 tables, etc.), and the current goal. "
        "Keep it under 150 words."
    )
    
    # Format messages for summary
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages[:-2]])
    
    try:
        summary = await ollama_chat(model, system, f"History to summarize:\n{history_text}")
        return summary.strip()
    except Exception as e:
        print(f"Summarization failed: {e}")
        return ""
