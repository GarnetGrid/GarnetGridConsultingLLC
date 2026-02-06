import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.reasoner.agent import reasoner_agent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat")
async def chat_reasoner(request: Request):
    """
    Reasoner Chat Endpoint (Streaming SSE).
    Expects JSON: { "message": "user query", "model": "optional_model_name" }
    """
    try:
        data = await request.json()
        user_input = data.get("message")
        model = data.get("model", "llama3.2")

        if not user_input:
            return {"error": "Message is required"}

        return StreamingResponse(
            reasoner_agent(user_input, model=model),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.error(f"Error in reasoner chat: {e}")
        return {"error": str(e)}
