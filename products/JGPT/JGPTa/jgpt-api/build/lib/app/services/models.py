from __future__ import annotations
from typing import List, Dict, AsyncGenerator
from app.rag.ollama_client import ollama_list_models, ollama_pull_model, _base_url
import httpx
import json

async def list_available_models() -> List[Dict]:
    """List all models available in the Ollama instance."""
    return await ollama_list_models()

async def pull_model_stream(model_name: str) -> AsyncGenerator[str, None]:
    """Pull a model and yield progress updates."""
    payload = {"name": model_name}
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{_base_url()}/api/pull", json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    yield line

async def delete_model(model_name: str) -> bool:
    """Delete a model."""
    payload = {"name": model_name}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.delete(f"{_base_url()}/api/delete", json=payload)
            r.raise_for_status()
            return True
    except:
        return False
