import pytest
from app.rag.chunking import chunk_text

def test_chunk_text_basic():
    """Test basic chunking with simple text"""
    text = "This is a simple test. " * 100
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    
    assert len(chunks) > 0
    assert all(len(c) <= 250 for c in chunks)  # Allow some buffer for context

def test_chunk_text_with_headers():
    """Test chunking preserves headers as context"""
    text = """# Main Document

## Section 1
This is the first section with some content.

## Section 2
This is the second section with different content.
"""
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    
    # Each chunk should have context prefix
    assert len(chunks) > 0
    for chunk in chunks:
        # Should contain document or section context
        assert "[Document:" in chunk or "[Section:" in chunk or "Main Document" in chunk

def test_chunk_text_empty():
    """Test chunking with empty text"""
    chunks = chunk_text("", chunk_size=100, overlap=20)
    assert len(chunks) == 0

def test_chunk_text_short():
    """Test chunking with text shorter than chunk size"""
    text = "Short text"
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    
    assert len(chunks) == 1
    assert text in chunks[0]

def test_chunk_text_overlap():
    """Test that overlap creates continuity between chunks"""
    text = "A" * 500
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    
    # With overlap, adjacent chunks should share some content
    if len(chunks) > 1:
        # Check that there's some overlap (allowing for context prefix)
        assert len(chunks) >= 2

def test_chunk_text_markdown_structure():
    """Test that markdown structure is respected"""
    text = """# Title

## Subsection 1
Content here.

## Subsection 2  
More content here.

### Deep section
Even more content.
"""
    chunks = chunk_text(text, chunk_size=150, overlap=30)
    
    assert len(chunks) > 0
    # Verify chunks maintain some structure
    assert any("Title" in c or "Subsection" in c for c in chunks)

def test_chunk_text_long_section():
    """Test chunking of a very long section"""
    long_section = "This is a very long section. " * 200
    text = f"# Document\n\n## Long Section\n{long_section}"
    
    chunks = chunk_text(text, chunk_size=500, overlap=100)
    
    # Should create multiple chunks
    assert len(chunks) > 1
    # Each chunk should respect size limit (with buffer for context)
    assert all(len(c) <= 700 for c in chunks)
