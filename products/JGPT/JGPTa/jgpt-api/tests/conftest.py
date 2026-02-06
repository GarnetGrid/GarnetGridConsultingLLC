import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

from app.db.models import Base

# Patch for TSVECTOR on SQLite
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import TSVECTOR

@compiles(TSVECTOR, "sqlite")
def compile_tsvector(type_, compiler, **kw):
    return "TEXT"

@pytest.fixture(scope="function")
def test_db():
    from sqlalchemy.pool import StaticPool
    """Create a fresh test database for each test"""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    # Ensure models are loaded
    import app.db.models
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    # Configure app's session to use test engine
    from app.db import session
    # Save original bind
    # sessionmaker doesn't expose 'bind' directly in a clean way if accessed via kw,
    # but we can re-create expectations. Or just use the original engine import.
    original_engine = session.engine
    
    # Update all references to SessionLocal to use the test engine
    session.SessionLocal.configure(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)
        # Restore original bind
        session.SessionLocal.configure(bind=original_engine)

@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with auth override"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.util.auth import get_current_user
    from app.db.models import User

    def mock_get_current_user():
        # Create a transient user object (not bound to session, but sufficient for route logic)
        return User(id=1, email="test@jgpt.com", role="admin", is_active=True)

    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Mock startup functions to prevent real DB connection
    import app.main as main_module
    import app.util.auth as auth_module
    
    # Save originals
    orig_init = main_module.init_db
    orig_seed = auth_module.seed_default_user
    
    # Patch where it is used
    main_module.init_db = lambda: None
    auth_module.seed_default_user = lambda: None
    
    with TestClient(app) as c:
        yield c
    
    # Restore
    app.dependency_overrides = {}
    main_module.init_db = orig_init
    auth_module.seed_default_user = orig_seed

@pytest.fixture(autouse=True)
def mock_ai_services():
    """Mock external AI services globally"""
    from unittest.mock import patch, AsyncMock
    
    # Define async generator for chat stream
    async def mock_stream(*args, **kwargs):
        # Initial chunk
        yield "Mocked AI response"
    
    # We patch only the usage sites (app.routes.*) so that unit tests 
    # which test the logic of ollama_client itself (e.g. test_models.py) 
    # can still import and test the real function (mocking httpx internally).
    
    # NOTE: app.routes.chat imports ollama_chat_stream at top-level.
    # Same for app.routes.ingest importing embed_one and scrape_url.
    
    with patch("app.routes.chat.ollama_chat_stream", side_effect=mock_stream), \
         patch("app.routes.ingest.embed_one", new_callable=AsyncMock) as mock_embed_ingest, \
         patch("app.routes.ingest.scrape_url", new_callable=AsyncMock) as mock_scrape_ingest, \
         patch("app.util.url_ingest.scrape_url", new_callable=AsyncMock) as mock_scrape_url_util:
            
        # Mock embedding (1024 dim)
        vector = [0.1] * 1024
        mock_embed_ingest.return_value = vector
        
        # Mock scrape
        mock_scrape_ingest.return_value = "Mocked page content."
        mock_scrape_url_util.return_value = "Mocked page content."
        
        yield
