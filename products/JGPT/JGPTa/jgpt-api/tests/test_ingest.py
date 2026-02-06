import pytest
from pathlib import Path
from app.util.ingest import infer_department, sha256_text

def test_infer_department_finance():
    """Test department inference for finance paths"""
    path = Path("kb/finance/report.md")
    assert infer_department(path) == "finance"

def test_infer_department_hr():
    """Test department inference for HR paths"""
    path = Path("kb/hr/policy.md")
    assert infer_department(path) == "hr"

def test_infer_department_it():
    """Test department inference for IT paths"""
    path = Path("kb/it/guide.md")
    assert infer_department(path) == "it"

def test_infer_department_supply():
    """Test department inference for supply chain paths"""
    path = Path("kb/supply/logistics.md")
    assert infer_department(path) == "supply"

def test_infer_department_default():
    """Test department inference defaults to 'all'"""
    path = Path("kb/other/document.md")
    assert infer_department(path) == "all"

def test_infer_department_nested():
    """Test department inference with nested paths"""
    path = Path("kb/finance/reports/2024/q1.md")
    assert infer_department(path) == "finance"

def test_sha256_text():
    """Test SHA256 hashing is consistent"""
    text = "Hello, World!"
    hash1 = sha256_text(text)
    hash2 = sha256_text(text)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 produces 64 hex characters

def test_sha256_text_different():
    """Test different texts produce different hashes"""
    hash1 = sha256_text("Text A")
    hash2 = sha256_text("Text B")
    
    assert hash1 != hash2
