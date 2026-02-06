import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.db.models import User
from app.util.auth import get_current_user, get_current_admin

# Mock User
mock_user = User(id=1, email="test@example.com", role="admin", is_active=True)

def mock_get_current_user():
    return mock_user

@pytest.fixture
def authorized_client(client, monkeypatch):
    """Client with mocked auth"""
    from app.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_current_admin] = mock_get_current_user
    yield client
    app.dependency_overrides = {}

def test_list_models(authorized_client):
    with patch("app.services.models.ollama_list_models", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [{"name": "llama2", "size": 1000}, {"name": "mistral", "size": 2000}]
        
        response = authorized_client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "llama2"

def test_pull_model_requires_admin(client):
    from app.main import app
    # Remove the global override for this test
    overrides = app.dependency_overrides.copy()
    app.dependency_overrides = {}
    
    try:
        # Without auth override, should fail
        response = client.post("/api/models/pull", json={"name": "llama2"})
        assert response.status_code in [401, 403]
    finally:
        # Restore overrides
        app.dependency_overrides = overrides

def test_delete_model(authorized_client):
    with patch("app.routes.models.delete_model", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        
        response = authorized_client.delete("/api/models/test-model")
        assert response.status_code == 200
        assert response.json()["deleted"] == "test-model"

@pytest.mark.asyncio
async def test_ollama_options():
    from app.rag.ollama_client import ollama_chat_stream
    with patch("httpx.AsyncClient.stream") as mock_stream:
        # We need to mock the context manager structure of client.stream
        mock_response = MagicMock()
        # make aiter_lines return an async iterator
        async def async_iter():
            yield b'{"message": {"content": "test"}}'
        mock_response.aiter_lines.side_effect = async_iter
        
        mock_stream.return_value.__aenter__.return_value = mock_response

        options = {"temperature": 0.7}
        gen = ollama_chat_stream("model", [], options=options)
        async for _ in gen: pass
        
        # Verify call args
        # call_args is (args, kwargs)
        # client.stream("POST", url, json=payload)
        # so check kwargs['json']
        _, kwargs = mock_stream.call_args
        assert "options" in kwargs["json"]
        assert kwargs["json"]["options"] == options
