from __future__ import annotations

import os
import httpx
import json

def _base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")

async def ollama_chat(model: str, system: str, user: str, timeout_s: float = 180.0) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        r = await client.post(f"{_base_url()}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()
    return ((data.get("message") or {}).get("content")) or ""

async def ollama_chat_stream(model: str, messages: list[dict], format: str = None, timeout_s: float = 180.0):
    """Generator for streaming responses from Ollama."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if format:
        payload["format"] = format

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
