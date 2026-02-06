import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.web_ingest import WebCrawler

@pytest.mark.asyncio
async def test_crawler_depth_0():
    client = AsyncMock()
    # Mock specific response
    client.get.return_value.text = "<html><body><a href='/foo'>Foo</a></body></html>"
    client.get.return_value.raise_for_status = MagicMock()
    
    crawler = WebCrawler(client, "example.com", max_depth=0) # depth 0 means just the page itself? Or depth 1 means page?
    # In my impl, max_depth=1 is default (process page). recursion happens if current < max_depth.
    # So max_depth=1 -> limit. 
    # Logic: if current_depth < self.max_depth: recurse.
    # call(0): 0 < 1? Yes. recurse(1).
    # call(1): 1 < 1? No. Stop.
    # So max_depth=1 means "Fetch this page, then fetch its children"? No.
    # Wait, if max_depth=1, and current=0. 0 < 1 is True. It fetches children (depth 1).
    # This means max_depth=1 is "1 level deep" (Page + Children). 
    # If I only want the page itself, max_depth should be 0? 
    # Let's check logic: process_page(current_depth=0). 
    # Recurse block: if current_depth < self.max_depth.
    # If max_depth=0: 0 < 0 is False. No recursion.
    # So max_depth=0 is "Just this page".
    # max_depth=1 is "This page + links on it".
    
    await crawler.process_page("http://example.com", 0)
    
    assert client.get.call_count == 1
    assert "http://example.com" in crawler.visited

@pytest.mark.asyncio
async def test_crawler_depth_1():
    client = AsyncMock()
    
    async def side_effect(url, **kwargs):
        resp = AsyncMock()
        resp.raise_for_status = MagicMock()
        if url == "http://example.com":
            resp.text = "<html><body><a href='/foo'>Foo</a></body></html>"
        elif url == "http://example.com/foo":
            resp.text = "<html><body>Content</body></html>"
        else:
            resp.text = ""
        return resp
        
    client.get.side_effect = side_effect
    
    crawler = WebCrawler(client, "example.com", max_depth=1)
    await crawler.process_page("http://example.com", 0)
    
    assert client.get.call_count == 2
    assert "http://example.com/foo" in crawler.visited
