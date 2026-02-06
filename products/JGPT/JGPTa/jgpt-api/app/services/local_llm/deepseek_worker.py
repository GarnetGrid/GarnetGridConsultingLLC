import logging
from app.services.local_llm.ollama_client import OllamaClient
import os

logger = logging.getLogger(__name__)
client = OllamaClient()

async def summarize_text(text: str) -> str:
    """Summarizes input text using DeepSeek."""
    if os.getenv("USE_LOCAL_LLM", "false").lower() != "true":
        logger.info("Local LLM disabled, skipping summarization.")
        return text[:500] + "..." if len(text) > 500 else text

    prompt = f"Summarize the following text concisely for technical reasoning:\n\n{text[:4000]}"
    summary = await client.generate_completion(prompt, system="You are a technical documentation assistant.")
    
    if summary:
        return summary
    return text[:200] + "... (Simplification due to LLM failure)"

async def expand_documentation(text: str) -> str:
    if os.getenv("USE_LOCAL_LLM", "false").lower() != "true":
        return text

    prompt = f"Expand the following documentation with technical details and examples:\n\n{text[:2000]}"
    expanded = await client.generate_completion(prompt, system="You are an expert technical writer.")
    return expanded or text

async def generate_reference_notes(text: str) -> str:
    if os.getenv("USE_LOCAL_LLM", "false").lower() != "true":
        return ""
        
    prompt = f"Generate key reference notes and metadata tags from this text:\n\n{text[:3000]}"
    notes = await client.generate_completion(prompt, system="You are a data archivist.")
    return notes or ""
