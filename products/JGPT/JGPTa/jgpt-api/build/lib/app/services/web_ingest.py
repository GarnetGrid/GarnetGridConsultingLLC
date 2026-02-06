import asyncio
import hashlib
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from typing import List, Dict, Tuple, Optional
import httpx
from readability import Document
from markdownify import markdownify as md
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_root_path() -> Path:
    """Get the project root path. Assumes this file is in app/services/."""
    # current file is app/services/web_ingest.py -> parent=services -> parent=app -> parent=jgpt-api
    return Path(__file__).resolve().parents[2]

KB_WEB = get_root_path() / "kb" / "web"
SOURCES_FILE = get_root_path() / "scripts" / "sources.yaml"

def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text[:80].strip("-") or "page"

def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]

def clean_markdown(md_text: str) -> str:
    # Fix common conversion artifacts
    md_text = md_text.replace("\r\n", "\n").replace("\r", "\n")
    md_text = re.sub(r"\n{3,}", "\n\n", md_text).strip()
    
    # Truncate very long lines to avoid issues with some vectorizers/tokenizers
    lines = []
    for ln in md_text.splitlines():
        if len(ln) > 5000:
            lines.append(ln[:5000] + " …")
        else:
            lines.append(ln)
    return "\n".join(lines)

async def fetch_url(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        resp = await client.get(url, headers={"User-Agent": UA}, follow_redirects=True, timeout=30.0)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

def process_html(html: str, url: str, preset_title: str = "") -> Tuple[str, str]:
    try:
        doc = Document(html)
        title = doc.short_title() or preset_title or url
        summary_html = doc.summary(html_partial=True)
        markdown_body = md(summary_html, heading_style="ATX")
        clean_body = clean_markdown(markdown_body)
        return title, clean_body
    except Exception as e:
        logger.error(f"Error processing HTML for {url}: {e}")
        return "Error", ""

async def save_to_kb(domain: str, title: str, url: str, body_md: str, force: bool = False) -> Optional[str]:
    parsed = urlparse(url)
    host = (parsed.netloc or "site").replace("www.", "")
    safe_title = slugify(title or host)
    fname = f"{safe_title}__{url_hash(url)}.md"
    
    out_dir = KB_WEB / domain / host
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / fname

    if out_path.exists() and not force:
        return None  # Skipped

    captured = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = f"""# {title.strip() if title else host}

**Source:** {url}
**Captured:** {captured}
**Domain:** {domain}

"""
    async with asyncio.Lock(): # Simple file lock mainly for thread safety if reused, though asyncio is single threaded
        out_path.write_text(header + body_md + "\n", encoding="utf-8")
    
    return str(out_path)

async def ingest_source(client: httpx.AsyncClient, domain: str, item: Dict, force: bool) -> str:
    url = item.get("url")
    if not url:
        return "skipped (no url)"
        
    title_preset = item.get("title", "")
    logger.info(f"Fetching {url}")
    
    html = await fetch_url(client, url)
    if not html:
        return "failed"
        
    title, body = process_html(html, url, title_preset)
    if not body:
        return "empty body"
        
    path = await save_to_kb(domain, title, url, body, force)
    if path:
        return "saved"
    return "skipped (exists)"

async def run_ingest(force: bool = False, max_pages: int = 0) -> Dict:
    if not SOURCES_FILE.exists():
        return {"ok": False, "error": "sources.yaml not found"}

    try:
        data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {"ok": False, "error": f"Invalid YAML: {e}"}

    tasks = []
    async with httpx.AsyncClient() as client:
        # Build task list
        count = 0
        for domain, items in data.items():
            if not items: continue
            for item in items:
                if max_pages > 0 and count >= max_pages:
                    break
                tasks.append(ingest_source(client, domain, item, force))
                count += 1
            if max_pages > 0 and count >= max_pages:
                break
        
        results = await asyncio.gather(*tasks)

    # Summarize
    summary = {
        "total": len(results),
        "saved": results.count("saved"),
        "skipped": results.count("skipped (exists)"),
        "failed": results.count("failed"),
    }
    return {"ok": True, "details": summary, "results": results}
