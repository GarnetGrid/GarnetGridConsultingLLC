from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import os
# Assuming we will move ollama_client here or import it.
# For now, importing from existing location to keep diff small, 
# but eventually this should be centralized.
from app.rag.ollama_client import ollama_chat

class ModelProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        """Generates a text response from the model."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Checks if the provider is available."""
        pass

class LocalDeepSeekProvider(ModelProvider):
    """Provider for local DeepSeek models via Ollama."""
    
    def __init__(self, default_model: str = "deepseek-r1:14b"):
        self.default_model = default_model
        
    async def generate(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        target_model = model or self.default_model
        return await ollama_chat(
            model=target_model,
            system=system_prompt,
            user=user_prompt
        )

    async def is_healthy(self) -> bool:
        # Simple check by trying to list models or a ping.
        # For now, we assume if imports work and server is up, it's healthy.
        # In production, we'd hit /api/tags or similar on the Ollama instance.
        try:
             # This is a mock health check. Real implementation would likely hit the API.
             # We can define a lighter weight check later.
             return True
        except Exception:
            return False

class OpenAIProvider(ModelProvider):
    """Provider for OpenAI cloud models."""
    
    def __init__(self, api_key: str = None, default_model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.default_model = default_model
        # We'd lazily import openai to avoid hard dependency if not used
        # import openai 
        # self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def generate(self, system_prompt: str, user_prompt: str, model: str = None) -> str:
        # Placeholder for OpenAI implementation
        # import openai
        # response = await self.client.chat.completions.create(...)
        # return response.choices[0].message.content
        return f"[Mock OpenAI Response for {user_prompt[:20]}...]"

    async def is_healthy(self) -> bool:
        return bool(self.api_key)
