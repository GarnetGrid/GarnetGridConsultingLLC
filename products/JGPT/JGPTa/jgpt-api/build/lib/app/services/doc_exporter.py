from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime
from app.db.models import Conversation, Message

EXPORT_DIR = Path(__file__).resolve().parents[2] / "exports"

def format_full_thread(conv: Conversation, messages: list[Message]) -> str:
    """Formats a conversation into a professional document."""
    title = conv.title or f"Chat {conv.id}"
    date_str = conv.created_at.strftime("%Y-%m-%d %H:%M:%S")
    
    md = f"# JGPT Research Report: {title}\n"
    md += f"**Date:** {date_str}  \n"
    md += f"**Model:** {conv.model} | **Mode:** {conv.mode}\n\n"
    md += "---\n\n"
    
    citations = set()
    
    for msg in messages:
        role = msg.role.capitalize()
        content = msg.content
        
        # Simple citation extractor (looking for [Source: link])
        import re
        cites = re.findall(r"\[Source:\s*(.+?)\]", content)
        for c in cites:
            citations.add(c)
            
        md += f"### {role}\n{content}\n\n"
        
    if citations:
        md += "---\n\n## Source Appendix\n"
        for i, source in enumerate(sorted(citations), 1):
            md += f"{i}. {source}\n"
            
    return md

def save_export(md_content: str, filename: str) -> str:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(x for x in filename if x.isalnum() or x in "._- ").strip()
    path = EXPORT_DIR / safe_name
    path.write_text(md_content, encoding="utf-8")
    return str(path)
