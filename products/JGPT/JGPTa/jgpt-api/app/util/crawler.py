import asyncio
import re
import logging
from pathlib import Path
from urllib.parse import urlparse, urljoin
from typing import List, Optional, Set, Dict
import httpx
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, 
                 start_url: str, 
                 allowed_domains: Set[str] = None, 
                 max_depth: int = 1, 
                 max_pages: int = 50,
                 concurrency: int = 5):
        self.start_url = start_url
        self.visited: Set[str] = set()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.results: List[Dict] = []
        
        parsed = urlparse(start_url)
        self.base_domain = parsed.netloc
        self.allowed_domains = allowed_domains or {self.base_domain}
        
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.sem = asyncio.Semaphore(concurrency)
        self.page_count = 0

    def is_allowed(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return False
            return parsed.netloc in self.allowed_domains
        except:
            return False

    def normalize_url(self, base: str, url: str) -> str:
        full = urljoin(base, url)
        parsed = urlparse(full)
        # Drop fragment, keep query
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{'?' + parsed.query if parsed.query else ''}"

    async def fetch(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        try:
            async with self.sem:
                resp = await client.get(url, follow_redirects=True, timeout=15.0)
                resp.raise_for_status()
                # Simple check for HTML
                ct = resp.headers.get("content-type", "").lower()
                if "text/html" not in ct and "application/xml" not in ct and "text/xml" not in ct:
                    return None
                return resp.text
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

    async def parse_sitemap(self, xml_content: str) -> List[str]:
        urls = []
        try:
            root = ET.fromstring(xml_content)
            # Handle potential namespaces
            for elem in root.iter():
                if 'loc' in elem.tag and elem.text:
                    urls.append(elem.text.strip())
        except Exception as e:
            logger.error(f"Sitemap parse error: {e}")
        return urls

    def extract_links(self, html: str, base_url: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a['href']
            url = self.normalize_url(base_url, href)
            if self.is_allowed(url):
                links.append(url)
        return links

    async def process_url(self, client: httpx.AsyncClient, url: str, depth: int):
        if url in self.visited or self.page_count >= self.max_pages:
            return
        
        self.visited.add(url)
        content = await self.fetch(client, url)
        if not content:
            return

        # Check if it looks like a sitemap
        if url.endswith(".xml") or "<urlset" in content or "<sitemapindex" in content:
            logger.info(f"Processing sitemap: {url}")
            child_urls = await self.parse_sitemap(content)
            for child in child_urls:
                if child not in self.visited:
                    # Treat sitemap entries as depth 0 or same depth? 
                    # Usually sitemaps are flat lists of pages.
                    await self.queue.put((child, depth)) # Keep depth?
            return

        # It's an HTML page
        self.page_count += 1
        self.results.append({
            "url": url,
            "content": content,
            "depth": depth
        })
        logger.info(f"Crawled ({self.page_count}/{self.max_pages}): {url}")

        if depth < self.max_depth:
            links = self.extract_links(content, url)
            for link in links:
                if link not in self.visited:
                    await self.queue.put((link, depth + 1))

    async def run(self):
        async with httpx.AsyncClient(headers={"User-Agent": "JGPT-Crawler/1.0"}) as client:
            # Seed queue
            await self.queue.put((self.start_url, 0))
            
            while not self.queue.empty() and self.page_count < self.max_pages:
                batch = []
                while not self.queue.empty() and len(batch) < 10:
                    batch.append(await self.queue.get())
                
                tasks = []
                for url, depth in batch:
                    tasks.append(self.process_url(client, url, depth))
                
                if tasks:
                    await asyncio.gather(*tasks)

        return self.results
