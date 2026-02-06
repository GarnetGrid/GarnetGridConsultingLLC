import logging
import httpx
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder"):
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url)
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.timeout = 60.0 # seconds

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama check failed: {e}")
            return False

    async def generate_completion(self, prompt: str, system: Optional[str] = None) -> Optional[str]:
        if not await self.is_available():
            logger.error("Ollama is not available.")
            return None

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending prompt to Ollama ({self.model})...")
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("response")
        except httpx.ReadTimeout:
            logger.error("Ollama request timed out.")
            return None
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None
