import pytest
from unittest.mock import AsyncMock, patch
from app.services.router.service import ModelRouter
from app.services.router.providers import LocalDeepSeekProvider, OpenAIProvider

@pytest.mark.asyncio
async def test_router_prefer_local_healthy():
    """Test that router selects local provider when preferred and healthy."""
    router = ModelRouter()
    
    # Mock providers
    router.local_provider = AsyncMock(spec=LocalDeepSeekProvider)
    router.local_provider.is_healthy.return_value = True
    router.local_provider.generate.return_value = "Local Response"
    
    router.cloud_provider = AsyncMock(spec=OpenAIProvider)
    
    response = await router.route_request("sys", "user", prefer_local=True)
    
    assert response == "Local Response"
    router.local_provider.generate.assert_called_once()
    router.cloud_provider.generate.assert_not_called()

@pytest.mark.asyncio
async def test_router_basic_fallback():
    """Test fallback to cloud when local is unhealthy."""
    router = ModelRouter()
    
    router.local_provider = AsyncMock(spec=LocalDeepSeekProvider)
    router.local_provider.is_healthy.return_value = False
    
    router.cloud_provider = AsyncMock(spec=OpenAIProvider)
    router.cloud_provider.generate.return_value = "Cloud Response"
    
    response = await router.route_request("sys", "user", prefer_local=True)
    
    assert response == "Cloud Response"
    router.local_provider.generate.assert_not_called()
    router.cloud_provider.generate.assert_called_once()

@pytest.mark.asyncio
async def test_router_exception_fallback():
    """Test fallback to cloud when local raises exception during generation."""
    router = ModelRouter()
    
    router.local_provider = AsyncMock(spec=LocalDeepSeekProvider)
    router.local_provider.is_healthy.return_value = True
    router.local_provider.generate.side_effect = Exception("Ollama Crash")
    
    router.cloud_provider = AsyncMock(spec=OpenAIProvider)
    router.cloud_provider.generate.return_value = "Cloud Response"
    
    response = await router.route_request("sys", "user", prefer_local=True)
    
    assert response == "Cloud Response"
    router.cloud_provider.generate.assert_called_once()
