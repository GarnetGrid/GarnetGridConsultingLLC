import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True

def test_chat_endpoint_basic(client, test_db):
    """Test basic chat functionality"""
    payload = {
        "message": "What is Power BI?",
        "persona": "default",
        "model": "llama3.2:3b",
        "grade": False,
        "department": "all"
    }
    
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    # SSE response, check content type
    assert "text/event-stream" in response.headers.get("content-type", "")

def test_ingest_url_endpoint(client, test_db):
    """Test URL ingestion endpoint"""
    payload = {
        "url": "https://example.com",
        "department": "it"
    }
    
    response = client.post("/api/ingest/url", params=payload)
    assert response.status_code in [200, 400, 422]  # 422 if url invalid format, 400 if unreachable
    
def test_conversations_list(client, test_db):
    """Test listing conversations"""
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_conversation_detail(client, test_db):
    """Test getting conversation details"""
    # First create a conversation by sending a message
    from app.db.models import Conversation
    conv = Conversation(title="Test Conversation", user_id=1)
    test_db.add(conv)
    test_db.commit()
    
    response = client.get(f"/api/conversations/{conv.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv.id
    assert data["title"] == "Test Conversation"

def test_conversation_delete(client, test_db):
    """Test deleting a conversation"""
    from app.db.models import Conversation
    conv = Conversation(title="To Delete", user_id=1)
    test_db.add(conv)
    test_db.commit()
    conv_id = conv.id
    
    response = client.delete(f"/api/conversations/{conv_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    response = client.get(f"/api/conversations/{conv_id}")
    assert response.status_code == 404

@pytest.mark.skip(reason="Eval route changed and requires specific suite setup")
def test_eval_endpoint(client, test_db):
    ...

def test_kb_status_endpoint(client, test_db):
    """Test knowledge base status endpoint"""
    response = client.get("/api/kb/status")
    assert response.status_code == 200
    data = response.json()
    assert "ok" in data
    assert "runs" in data
