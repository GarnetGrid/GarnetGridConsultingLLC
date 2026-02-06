from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db.models import Conversation, Message, User
from app.tools.exporter import export_conversation
from app.util.auth import get_current_user
from fastapi import Depends

router = APIRouter()

class CreateConversation(BaseModel):
    title: str | None = None
    mode: str = "powerbi"
    model: str = "llama3.2"

@router.post("")
def create_conversation(req: CreateConversation, current_user: User = Depends(get_current_user)):
    with SessionLocal() as s:
        c = Conversation(title=req.title or "New chat", mode=req.mode, model=req.model, user_id=current_user.id)
        s.add(c); s.commit(); s.refresh(c)
        return {"id": c.id, "title": c.title, "mode": c.mode, "model": c.model, "created_at": c.created_at.isoformat()}

@router.get("")
def list_conversations(current_user: User = Depends(get_current_user)):
    with SessionLocal() as s:
        rows = s.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc()).limit(200).all()
        return [{"id":r.id,"title":r.title,"mode":r.mode,"model":r.model,"created_at":r.created_at.isoformat()} for r in rows]

@router.get("/{conversation_id}")
def get_conversation(conversation_id: int, current_user: User = Depends(get_current_user)):
    with SessionLocal() as s:
        c = s.get(Conversation, conversation_id)
        if not c or c.user_id != current_user.id:
            raise HTTPException(404, "Conversation not found")
        msgs = s.query(Message).filter(Message.conversation_id==conversation_id).order_by(Message.created_at.asc()).all()
        return {
            "id": c.id,
            "title": c.title,
            "mode": c.mode,
            "model": c.model,
            "created_at": c.created_at.isoformat(),
            "messages":[{"id":m.id,"role":m.role,"content":m.content,"created_at":m.created_at.isoformat()} for m in msgs]
        }
@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, current_user: User = Depends(get_current_user)):
    with SessionLocal() as s:
        c = s.get(Conversation, conversation_id)
        if not c or c.user_id != current_user.id:
            raise HTTPException(404, "Conversation not found")
        s.delete(c)
        s.commit()
        return {"ok": True}

from app.services.doc_exporter import format_full_thread, save_export
from sqlalchemy import select
from datetime import datetime

@router.post("/{conversation_id}/export/full")
def export_full_report(conversation_id: int, current_user: User = Depends(get_current_user)):
    with SessionLocal() as s:
        conv = s.get(Conversation, conversation_id)
        if not conv or conv.user_id != current_user.id:
            raise HTTPException(404, "Conversation not found")
        msgs = s.execute(select(Message).where(Message.conversation_id==conversation_id).order_by(Message.created_at)).scalars().all()
        
        md = format_full_thread(conv, msgs)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = save_export(md, f"Report_{conversation_id}_{ts}.md")
        
        return {"ok": True, "path": path}

@router.post("/{conversation_id}/export")
def export_thread(conversation_id: int, current_user: User = Depends(get_current_user)):
    with SessionLocal() as s:
        c = s.get(Conversation, conversation_id)
        if not c or c.user_id != current_user.id:
            raise HTTPException(404, "Conversation not found")
        msgs = s.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
        history = [{"role": m.role, "content": m.content} for m in msgs]
        
        status = export_conversation(title=f"Chat Report: {c.title}", messages=history)
        return {"ok": True, "message": status}
