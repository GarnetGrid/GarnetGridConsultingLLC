import asyncio
import sys
import os

# Add app to path
sys.path.append(os.getcwd())

from app.util.crawler import WebCrawler
from app.db.session import SessionLocal
from app.db.models import Document, Chunk
from app.util.ingest import sha256_text
from app.rag.chunking import chunk_text
from app.rag.embeddings import embed_one
from sqlalchemy import select, delete

async def test():
    target = "https://example.org"
    print(f"Starting crawl of {target}...")
    crawler = WebCrawler(start_url=target, max_depth=1, max_pages=2)
    results = await crawler.run()
    
    if not results:
        print("No pages found! Check network or parser.")
        return

    # Simulate Ingest
    with SessionLocal() as s:
        for page in results:
            url = page['url']
            print(f"Ingesting {url}...")
            text = page['content'] 
            import re
            text = re.sub(r'<[^>]+>', '', text).strip()
            
            h = sha256_text(text)
            
            existing = s.execute(select(Document).where(Document.source_path == url)).scalar_one_or_none()
            if existing:
                s.execute(delete(Chunk).where(Chunk.document_id == existing.id))
                existing.content = text
                existing.content_hash = h
                doc_id = existing.id
            else:
                doc = Document(source_path=url, domain="test", department="it", mime_type="text/html", content_hash=h, content=text)
                s.add(doc); s.commit(); s.refresh(doc)
                doc_id = doc.id
            
            chunks = chunk_text(text, 1000, 100)
            if not chunks: chunks = ["Empty"]
            
            embeddings = await asyncio.gather(*[embed_one(c) for c in chunks])
            for i, (c, emb) in enumerate(zip(chunks, embeddings)):
                s.add(Chunk(document_id=doc_id, chunk_index=i, text=c, embedding=emb))
            s.commit()
            print(f"Success! Ingested {len(chunks)} chunks for {url}")

if __name__ == "__main__":
    asyncio.run(test())
