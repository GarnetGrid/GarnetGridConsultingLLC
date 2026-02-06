from __future__ import annotations

import os
import asyncio
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.util.auth import get_current_user, get_current_admin
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


# Environment-controlled CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup() -> None:
    init_db()
    # Optional KB hot-reload watcher (polling). Enable with KB_WATCH=1
    if kb_watch_enabled():
        poll = int(os.getenv("KB_WATCH_POLL", "10"))
        asyncio.create_task(kb_watch_loop(poll_seconds=poll))

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"], dependencies=[Depends(get_current_user)])
app.include_router(conv_router, prefix="/api/conversations", tags=["Conversations"], dependencies=[Depends(get_current_user)])
app.include_router(ingest_router, prefix="/api/ingest", tags=["Ingestion"], dependencies=[Depends(get_current_user)])
app.include_router(kb_router, prefix="/api/kb", tags=["Knowledge Base"], dependencies=[Depends(get_current_user)])
app.include_router(kb_sources_router, prefix="/api/kb", tags=["Knowledge Base"], dependencies=[Depends(get_current_user)])
app.include_router(eval_router, prefix="/api/eval", tags=["Evaluation"], dependencies=[Depends(get_current_user)])
app.include_router(health_router, prefix="/api/health", tags=["System"])
app.include_router(debug_router, prefix="/api/debug", tags=["Debug"], dependencies=[Depends(get_current_user)])
app.include_router(images_router, prefix="/api/images", tags=["Assets"], dependencies=[Depends(get_current_user)])
app.include_router(models_router, prefix="/api/models", tags=["Models"], dependencies=[Depends(get_current_user)])
app.include_router(tools_router, prefix="/api/tools", tags=["Tools"], dependencies=[Depends(get_current_user)])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])
