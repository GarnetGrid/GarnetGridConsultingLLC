import asyncio
import hashlib
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Tuple, Optional, Set
import httpx
from readability import Document
from markdownify import markdownify as md
import yaml
import xml.etree.ElementTree as ET

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_root_path() -> Path:
    """Get the project root path. Assumes this file is in app/services/."""
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

from app.rag.ollama_client import ollama_chat

async def classify_content(text: str) -> str:
    """Classify content into a department using LLM."""
    try:
        snippet = text[:1000].replace("\n", " ")
        prompt = f"""
        Classify this text into one of: Finance, HR, IT, Supply, Sales, General.
        Return ONLY the category name.
        
        Text: {snippet} ...
        """
        resp = await ollama_chat(model="llama3.2", system="You are a classifier.", user=prompt)
        dept = resp.strip().lower()
        if dept not in ["finance", "hr", "it", "supply", "sales"]:
            return "general"
        return dept
    except:
        return "general"

async def save_to_kb(domain: str, title: str, url: str, body_md: str, force: bool = False, department: str = "general") -> Optional[str]:
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
**Department:** {department}

"""
    async with asyncio.Lock(): 
        out_path.write_text(header + body_md + "\n", encoding="utf-8")
    
    return str(out_path)


class WebCrawler:
    def __init__(self, client: httpx.AsyncClient, domain: str, max_depth: int = 1, force: bool = False, semaphore: Optional[asyncio.Semaphore] = None):
        self.client = client
        self.domain = domain
        self.max_depth = max_depth
        self.force = force
        self.visited: Set[str] = set()
        self.results: List[str] = []
        self.semaphore = semaphore or asyncio.Semaphore(5)

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and belongs to the same domain scope ideally."""
        # For simplicity, we allow any http/https URL.
        # In strict mode, we might want to restrict to the seed domain.
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https")

    def normalize_url(self, base: str, url: str) -> str:
        full = urljoin(base, url)
        parsed = urlparse(full)
        # remove fragment
        return parsed.scheme + "://" + parsed.netloc + parsed.path + (("?" + parsed.query) if parsed.query else "")

    async def fetch(self, url: str) -> Optional[str]:
        try:
            resp = await self.client.get(url, headers={"User-Agent": UA}, follow_redirects=True, timeout=30.0)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None

    def extract_links(self, html: str, base_url: str) -> List[str]:
        # Simple regex based extraction to avoid heavy parsing just for links
        # This finds href="..."
        links = set()
        # Regex is a bit naive but robust enough for simple crawling. 
        # Matches href="url" or href='url'
        pattern = re.compile(r'href=["\'](.*?)["\']', re.IGNORECASE)
        for match in pattern.finditer(html):
            raw_url = match.group(1)
            # Filter distinct non-navigation links if possible? 
            # For now, get everything that looks like a webpage
            full_url = self.normalize_url(base_url, raw_url)
            if self.is_valid_url(full_url):
                 links.add(full_url)
        return list(links)

    async def process_page(self, url: str, current_depth: int, preset_title: str = ""):
        if url in self.visited:
            return
        self.visited.add(url)
        
        async with self.semaphore:
            logger.info(f"Crawling {url} (depth {current_depth})")
            html = await self.fetch(url)
        
        if not html:
            self.results.append("failed")
            return

        # Process and Save
        try:
            doc = Document(html)
            title = doc.short_title() or preset_title or url
            summary_html = doc.summary(html_partial=True)
            markdown_body = md(summary_html, heading_style="ATX")
            clean_body = clean_markdown(markdown_body)
            
            # Classification
            dept = await classify_content(clean_body)
            
            # Save
            path = await save_to_kb(self.domain, title, url, clean_body, self.force, department=dept)
            if path:
                self.results.append("saved")
            else:
                self.results.append("skipped (exists)")
                
        except Exception as e:
            logger.error(f"Error processing HTML for {url}: {e}")
            self.results.append("error")
            return

        # Recurse
        if current_depth < self.max_depth:
            # Extract links
            links = self.extract_links(html, url)
            
            # Filter links to stay within same domain roughly?
            # Let's restrict to sub-paths or same domain to avoid crawling the whole internet
            base_domain = urlparse(url).netloc
            
            sub_tasks = []
            for link in links:
                if link not in self.visited:
                    link_domain = urlparse(link).netloc
                    # Only follow internal links
                    if link_domain == base_domain:
                        sub_tasks.append(self.process_page(link, current_depth + 1))
            
            if sub_tasks:
                await asyncio.gather(*sub_tasks)

    async def fetch_sitemap(self, url: str) -> List[str]:
        """Fetch a sitemap and return URLs."""
        try:
            logger.info(f"Fetching sitemap: {url}")
            content = await self.fetch(url)
            if not content:
                return []
            
            root = ET.fromstring(content)
            urls = []
            
            # Robust extraction of text from any 'loc' tag regardless of namespace
            for elem in root.iter():
                if 'loc' in elem.tag and elem.text:
                    urls.append(elem.text.strip())
                    
            return list(set(urls))
        except Exception as e:
            logger.error(f"Error parsing sitemap {url}: {e}")
            return []

    async def run(self, item: Dict):
        """Entry point for a source item."""
        url = item.get("url")
        src_type = item.get("type", "page")
        
        if not url:
            self.results.append("skipped (no url)")
            return

        if src_type == "sitemap":
            sitemap_urls = await self.fetch_sitemap(url)
            logger.info(f"Sitemap {url} found {len(sitemap_urls)} URLs")
            
            limit = item.get("limit", 20)
            target_urls = sitemap_urls[:limit]
            
            tasks = []
            for u in target_urls:
                # Sitemaps usually point to pages, we treat them as depth=0 starts (or depth=1?)
                # If we want to crawl FROM those pages, we use max_depth.
                # Assuming sitemap items are the "leaves" we want, but if max_depth > 1 we might go deeper.
                # For safety, let's treat sitemap entries as individual pages with the configured max_depth?
                # Actually, usually sitemaps are comprehensive. Let's just process them.
                tasks.append(self.process_page(u, current_depth=0)) # Reset depth for each sitemap entry?
            
            if tasks:
                await asyncio.gather(*tasks)
                
        else:
            # Single page start
            await self.process_page(url, current_depth=0, preset_title=item.get("title", ""))


async def run_ingest(force: bool = False, max_pages: int = 0) -> Dict:
    if not SOURCES_FILE.exists():
        return {"ok": False, "error": "sources.yaml not found"}

    try:
        data = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {"ok": False, "error": f"Invalid YAML: {e}"}

    all_results = []
    
    async with httpx.AsyncClient() as client:
        # Global semaphore for all tasks
        sem = asyncio.Semaphore(5)
        
        jobs = []
        crawlers = []
        
        for domain, items in data.items():
            if not items: continue
            
            for item in items:
                item_depth = item.get("depth", 1) 
                
                crawler = WebCrawler(client, domain, max_depth=item_depth, force=force, semaphore=sem)
                crawlers.append(crawler)
                jobs.append(crawler.run(item))
        
        await asyncio.gather(*jobs)
        
        for c in crawlers:
            all_results.extend(c.results)

    # Summarize
    summary = {
        "total": len(all_results),
        "saved": all_results.count("saved"),
        "skipped": all_results.count("skipped (exists)"),
        "failed": all_results.count("failed"),
    }
    return {"ok": True, "details": summary, "results": all_results}
