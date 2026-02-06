import httpx
from bs4 import BeautifulSoup
import re

async def scrape_url(url: str) -> str:
    """Fetch and clean markdown-like text from a URL."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        html = r.text

    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Simple text extraction
    text = soup.get_text(separator="\n")
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)
    
    return text

def convert_to_markdown(html_content: str) -> str:
    """Basic HTML to Markdown conversion for RAG."""
    # Note: In a real product, use a library like 'markdownify' or 'trafilatura'
    # For this demo, we'll use a very simple regex approach
    md = html_content
    # Replace headers
    md = re.sub(r'<h1.*?>(.*?)</h1>', r'# \1\n', md, flags=re.I|re.S)
    md = re.sub(r'<h2.*?>(.*?)</h2>', r'## \1\n', md, flags=re.I|re.S)
    md = re.sub(r'<h3.*?>(.*?)</h3>', r'### \1\n', md, flags=re.I|re.S)
    # Strip remaining tags
    md = re.sub(r'<.*?>', '', md, flags=re.S)
    return md
