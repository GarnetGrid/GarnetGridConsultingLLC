from typing import Optional
from app.services.router.providers import ModelProvider, LocalDeepSeekProvider, OpenAIProvider

class ModelRouter:
    """
    Routes prompt requests to the appropriate provider based on availability
    and task type.
    """
    
    def __init__(self):
        self.local_provider = LocalDeepSeekProvider()
        self.cloud_provider = OpenAIProvider()
        
    async def route_request(self, 
                          system_prompt: str, 
                          user_prompt: str, 
                          task_type: str = "general",
                          prefer_local: bool = True) -> str:
        """
        Routes the request.
        
        Args:
            task_type: 'reasoning', 'creative', 'coding', 'general'
            prefer_local: If True, attempts to use local DeepSeek first.
        """
        
        # Strategy:
        # 1. If prefer_local is True and Local is healthy -> Local
        # 2. Else -> Cloud
        # 3. Fallback -> Cloud (if Local fails)
        
        if prefer_local:
            if await self.local_provider.is_healthy():
                try:
                    # In a real app, we might check queue depth here too
                    return await self.local_provider.generate(system_prompt, user_prompt)
                except Exception as e:
                    print(f"Local provider failed, falling back to cloud: {e}")
                    # Fallthrough to cloud
            else:
                print("Local provider unhealthy, using cloud.")
        
        # Fallback or default to cloud
        return await self.cloud_provider.generate(system_prompt, user_prompt)

# Singleton instance to be used by the app
router = ModelRouter()
