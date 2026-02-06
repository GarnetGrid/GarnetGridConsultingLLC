# JGPT Changelog

## 0.4.0 (Productization)
- Unified Packaging: Added root-level `docker-compose.yml` to orchestrate DB, API, and Web.
- Production UI: Created multi-stage `Dockerfile` for `jgpt-web` with build-time environment support.
- Developer Cockpit: Improved `Makefile` with `setup`, `up`, and `ingest` commands.
- Documentation Overhaul: Created professional `README.md`, `ARCHITECTURE.md`, and added MIT `LICENSE`.
- Environment Standardization: Unified environment variable naming across the entire stack.
- Security Persistence: Added persistent storage volume for AI-processed images and assets.
- Route Cleanliness: Standardized API routing with proper tags and prefixes in Swagger.

## 0.2.0
- Add CORS middleware (CORS_ORIGINS) to prevent browser preflight failures
- Fix RAG retrieve() return mismatch in chat route
- Add /debug/status endpoint (DB + Ollama + KB stats)
- Add RAG meta into tool_trace
- Truncate tool outputs to prevent prompt bloat
- Frontend: add timeout helper + ensure /chat URL has no trailing slash


## 0.2.1
- Upgrade Power BI system prompt: strict DAX contract + fact-table min/max date default
- Add Power BI KB starter pack (date table, time intelligence, measure patterns, modeling, Power Query)


## 0.3.0
- Add eval questions + judge-based evaluation pipeline
- Add D365FO KB pattern pack and move KB under jgpt-api/kb for ingest
- Add KB hot-reload watcher + /kb/status + /kb/reload
- Add answer quality scoring (heuristic) and optional LLM grading; UI toggle
- Add Ollama embeddings provider (mxbai-embed-large) for fully local RAG
- Add optional Ollama reranker (RERANK=1) to improve retrieval quality
- Add KB distillation script (Ollama) to expand KB from raw sources
- Add eval question sets (Power BI + D365FO)
- Add heuristic answer grading/confidence in chat responses (grade=true)
