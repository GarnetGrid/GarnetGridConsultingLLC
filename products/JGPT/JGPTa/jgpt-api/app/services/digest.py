import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import Document
from app.rag.ollama_client import ollama_chat

logger = logging.getLogger(__name__)

async def generate_daily_digest(hours: int = 24) -> str:
    """
    Generates a summary of documents ingested in the last N hours.
    """
    session = SessionLocal()
    try:
        # Calculate time window
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        # Fetch documents
        stmt = select(Document).where(Document.created_at >= since).where(Document.domain == "web")
        docs = session.execute(stmt).scalars().all()
        
        if not docs:
            logger.info("No new documents found for digest.")
            return "No new documents found."

        # Prepare context for LLM
        # We limit the context to avoid context window explosion. 
        # For a real system, we might need a map-reduce summarization if many docs.
        # Here we take the first 1000 chars of each title/content.
        context_parts = []
        for d in docs:
            snippet = d.content[:500].replace("\n", " ")
            context_parts.append(f"- Source: {d.source_path}\n  Content: {snippet}...")
            
        full_context = "\n\n".join(context_parts)
        
        prompt = f"""
        You are an intelligent news analyst. 
        Below is a list of news articles and documents captured in the last {hours} hours.
        
        Generate a concise "Daily Digest" executive summary. 
        - Group related topics.
        - Highlight key events.
        - Be professional and brief.
        
        Incoming Data:
        {full_context}
        """
        
        summary = await ollama_chat(
            model="llama3.2",
            system="You are a helpful news analyst.",
            user=prompt
        )
        
        # In a real app, we'd email this or save it to a 'Digest' table.
        # For now, we'll log it and maybe saving it as a special Document? 
        # Let's just log it and return it.
        logger.info(f"Generated Digest: \n{summary}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating digest: {e}")
        return f"Error: {e}"
    finally:
        session.close()
