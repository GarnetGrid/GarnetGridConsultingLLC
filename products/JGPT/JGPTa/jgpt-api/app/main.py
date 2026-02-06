from __future__ import annotations

import os
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.util.auth import get_current_user, get_current_admin
from app.middleware.auth import verify_client_access
from app.routes import auth_routes

from app.db.init_db import init_db
from app.routes.health import router as health_router
from app.routes.chat import router as chat_router
from app.routes.ingest import router as ingest_router
from app.routes.conversations import router as conv_router
from app.routes.eval import router as eval_router
from app.routes.kb import router as kb_router
from app.routes.kb_sources import router as kb_sources_router
from app.routes.debug import router as debug_router
from app.routes.images import router as images_router
from app.routes.admin import router as admin_router
from app.routes.models import router as models_router
from app.routes.tools import router as tools_router
from app.util.kb_watch import kb_watch_enabled, kb_watch_loop

# Rate Limiting
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.util.limiter import limiter

app = FastAPI(
    title="JGPT API",
    version="0.3.0",
    description="""
## JGPT - Enterprise RAG System

A production-ready Retrieval-Augmented Generation system with:
- **Semantic Chunking**: Intelligent document processing preserving context
- **Department-Aware Retrieval**: Knowledge siloing for organizational structure
- **Agentic Workflows**: Multi-step reasoning with tool use
- **Truth Audit**: Fact-checking with confidence scoring
- **Streaming Responses**: Real-time SSE-based chat
- **Conversation Management**: Full history tracking and export

### Key Features
- Vector + keyword hybrid search with pgvector
- Ollama integration for local LLM inference
- Professional document export (Markdown reports)
- Knowledge base hot-reloading
- Comprehensive evaluation metrics
    """,
    contact={
        "name": "JGPT Team",
        "url": "https://github.com/yourorg/jgpt",
    },
    license_info={
        "name": "MIT",
    },
)

# Register Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Environment-controlled CORS
# Environment-controlled CORS
# Default to ONLY localhost:3000 for strict security in dev/prod unless overridden.
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://jgpt.garnetgrid.com")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

# If we have specific origins, we MUST use them when allow_credentials=True
# FastAPI/Starlette will error if allow_origins=["*"] and allow_credentials=True
print(f"CORS: Allowing origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.on_event("startup")
async def startup() -> None:
    from app.util.auth import seed_default_user
    init_db()
    seed_default_user()
    
    # Initialize Scheduler
    from app.cron.scheduler import start_scheduler, scheduler
    from app.cron.news_scraper import scrap_news_job
    from app.cron.digest_job import digest_job
    
    start_scheduler()
    # Schedule the news scraper to run every 24 hours
    if not scheduler.get_job("news_scraper"):
        scheduler.add_job(scrap_news_job, "interval", hours=24, id="news_scraper", replace_existing=True)

    # Schedule Digest to run every 24 hours (e.g., at 8 AM UTC ideally, but interval is fine for now)
    # Let's offset it from the scraper so it has data.
    if not scheduler.get_job("daily_digest"):
        scheduler.add_job(digest_job, "interval", hours=24, id="daily_digest", replace_existing=True) 

    # Optional KB hot-reload watcher (polling). Enable with KB_WATCH=1
    if kb_watch_enabled():
        poll = int(os.getenv("KB_WATCH_POLL", "10"))
        asyncio.create_task(kb_watch_loop(poll_seconds=poll))

from app.routes.connections import router as connections_router

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
# For now, we enforce client access on Chat and Reasoning, or all?
# Plan says strict isolation. Let's add it to chat for now as a test.
# Actually, if we use API Key, we might not have a JWT 'user'. 
# We need to handle both or determine precedence.
# Middleware injects client_id. 
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
app.include_router(conv_router, prefix="/api/conversations", tags=["Conversations"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
app.include_router(ingest_router, prefix="/api/ingest", tags=["Ingestion"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
app.include_router(kb_router, prefix="/api/kb", tags=["Knowledge Base"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
app.include_router(kb_sources_router, prefix="/api/kb", tags=["Knowledge Base"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
app.include_router(eval_router, prefix="/api/eval", tags=["Evaluation"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
app.include_router(health_router, prefix="/api/health", tags=["System"])
app.include_router(debug_router, prefix="/api/debug", tags=["Debug"], dependencies=[Depends(get_current_user)])
app.include_router(images_router, prefix="/api/images", tags=["Assets"], dependencies=[Depends(get_current_user)])
app.include_router(models_router, prefix="/api/models", tags=["Models"], dependencies=[Depends(get_current_user)])
app.include_router(tools_router, prefix="/api/tools", tags=["Tools"], dependencies=[Depends(get_current_user)])
app.include_router(connections_router, prefix="/api/connections", tags=["Connections"], dependencies=[Depends(get_current_admin)])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])

from app.routes.powerbi import router as powerbi_router
app.include_router(powerbi_router, prefix="/api/powerbi", tags=["PowerBI"], dependencies=[Depends(get_current_user)])

from app.routes.reason import router as reason_router
app.include_router(reason_router, prefix="/api/reason", tags=["Reasoning"], dependencies=[Depends(get_current_user), Depends(verify_client_access)])
