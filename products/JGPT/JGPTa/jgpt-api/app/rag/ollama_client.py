from __future__ import annotations

import os
import httpx
import json

def _base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")

async def ollama_chat(model: str, system: str, user: str, timeout_s: float = 180.0, options: dict = None) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
    }
    if options:
        payload["options"] = options

    async with httpx.AsyncClient(timeout=timeout_s) as client:
        r = await client.post(f"{_base_url()}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    return ((data.get("message") or {}).get("content")) or ""

async def ollama_chat_stream(model: str, messages: list[dict], format: str = None, timeout_s: float = 180.0, options: dict = None):
    """Generator for streaming responses from Ollama."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if format:
        payload["format"] = format
    if options:
        payload["options"] = options

    async with httpx.AsyncClient(timeout=timeout_s) as client:
        async with client.stream("POST", f"{_base_url()}/api/chat", json=payload) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
                if chunk.get("done"):
                    break

async def ollama_embed(model: str, text: str, timeout_s: float = 60.0) -> list[float]:
    # Ollama embeddings endpoint: /api/embeddings
    payload = {"model": model, "prompt": text}
    print(f"DEBUG: Embedding text length: {len(text)}")
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        r = await client.post(f"{_base_url()}/api/embeddings", json=payload)
        if r.status_code != 200:
            print(f"Ollama Error: {r.status_code} - {r.text}")
        r.raise_for_status()
        data = r.json()
    emb = data.get("embedding")
    if not isinstance(emb, list):
        raise RuntimeError(f"Ollama embeddings returned unexpected shape: {type(emb)}")
    return emb

async def ollama_list_models() -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_base_url()}/api/tags")
        r.raise_for_status()
        return r.json().get("models", [])

async def ollama_pull_model(model: str) -> None:
    """Trigger a pull. This is usually long running."""
    payload = {"name": model}
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{_base_url()}/api/pull", json=payload) as response:
             async for line in response.aiter_lines():
                 if line:
                     # Just yield or log progress? For now, we just consume it to wait for completion if awaited.
                     # But this function returns None, so it consumes fully.
                     pass 

