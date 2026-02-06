import os
from pathlib import Path
from datetime import datetime

EXPORT_DIR = Path(__file__).resolve().parents[3] / "exports"

def save_snippet(title: str, content: str, category: str = "general", format: str = "md") -> str:
    """
    Saves a snippet of text/code to a local file.
    format: 'md' or 'html'
    """
    if not EXPORT_DIR.exists():
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    safe_title = "".join([c if c.isalnum() else "_" for c in title]).strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = "html" if format == "html" else "md"
    filename = f"{timestamp}_{safe_title}.{extension}"
    target = EXPORT_DIR / filename
    
    if format == "html":
        html_content = content.replace("\n", "<br>")
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 20px; }}
                h1 {{ border-bottom: 2px solid #ff2a6d; padding-bottom: 10px; color: #1a1a2e; }}
                .meta {{ color: #666; font-size: 0.9em; margin-bottom: 30px; }}
                pre {{ background: #f4f4f4; padding: 15px; border-radius: 8px; overflow-x: auto; }}
                .content {{ background: white; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="meta">Category: {category} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
            <div class="content">{html_content}</div>
        </body>
        </html>
        """
        target.write_text(body, encoding="utf-8")
    else:
        header = f"# {title}\n\n**Category:** {category}\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n"
        target.write_text(header + content, encoding="utf-8")
    
    return f"Successfully saved to {filename} in the exports directory."

def export_conversation(title: str, messages: list[dict]):
    """Formats a full conversation history into a professional report."""
    content = ""
    for m in messages:
        role = m.get("role", "user").upper()
        content += f"### {role}\n{m.get('content', '')}\n\n---\n\n"
    
    return save_snippet(title, content, category="Report", format="md")
