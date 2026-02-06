from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.util.auth import get_current_admin, get_current_user
from app.db.models import User
from app.services.models import list_available_models, pull_model_stream, delete_model
from pydantic import BaseModel

router = APIRouter()

class PullRequest(BaseModel):
    name: str

@router.get("")
async def list_models(current_user: User = Depends(get_current_user)):
    """List available LLM models."""
    return await list_available_models()

@router.post("/pull")
async def pull_model_route(req: PullRequest, current_user: User = Depends(get_current_admin)):
    """Pull a new model from Ollama library. Admin only."""
    return StreamingResponse(pull_model_stream(req.name), media_type="application/x-ndjson")

@router.delete("/{name}")
async def delete_model_route(name: str, current_user: User = Depends(get_current_admin)):
    """Delete a model. Admin only."""
    success = await delete_model(name)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete model")
    return {"ok": True, "deleted": name}
