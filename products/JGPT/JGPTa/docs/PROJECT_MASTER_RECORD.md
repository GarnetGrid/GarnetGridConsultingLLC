# 📔 JGPT: Master Project Record & SOP

This document provides a comprehensive, high-depth record of every development phase, feature implementation, and architectural decision made since the project's inception.

---

## 🏗️ Phase 1: Foundation (B.L.A.S.T. Protocol)
The project began under the **B.L.A.S.T. Protocol**, focusing on building a deterministic, self-healing automation foundation.
- **Initial Stack**: FastAPI backend, Next.js frontend, and PostgreSQL with `pgvector`.
- **Core Vision**: Create a private, enterprise-grade RAG system capable of handling complex domain knowledge (Power BI, D365FO).

## 🛠️ Phase 2: Reliability & Specialization (v0.2.x)
Focus shifted to system reliability and specific domain expertise.
- **CORS & Middleware**: Implemented environment-controlled CORS to permit secure browser communication.
- **Power BI Intelligence**: Integrated a specialized DAX contract and fact-table logic into the system prompt.
- **Observability**: Added `/debug/status` for real-time monitoring of Database, Ollama, and Knowledge Base health.
- **Tool Tracing**: Implemented RAG metadata injection into tool traces for better transparency in agentic reasoning.

## 🧠 Phase 3: Intelligence & Local RAG (v0.3.x)
A major leap in RAG performance and offline capability.
- **Local Embeddings**: Switched to **Ollama** (`mxbai-embed-large`) as the primary embedding provider for 100% privacy.
- **Advanced Retrieval**: Added **LLM Reranking** and **Semantic Chunking** to significantly reduce hallucinations.
- **KB Hot-Reloading**: Implemented a file-watcher that automatically updates the vector DB when `kb/` files change.
- **Evaluation Pipeline**: Built a judge-based eval system utilizing questions in `.jsonl` format to benchmark answer quality.
- **Vision Support**: Added the ability to extract and describe images from PDFs and DOCX files using local vision models.

## 🔐 Phase 4: Security Hardening
Before moving to production, the system underwent a security audit.
- **API Key Security**: Implemented strict header-based authentication (`X-API-Key`).
- **Input Sanitization**: Hardened routes to prevent prompt injection and unauthorized file access.
- **Persistent Storage**: Refined volume mappings to ensure encrypted or secured storage for vectorized assets.

## 🚀 Phase 5: Productization & Packaging (v0.4.0)
The final step was transforming the repository into a "Ready to Sell" package.
- **Unified Orchestration**: Created a root `docker-compose.yml` for zero-friction deployment of the whole stack.
- **Next.js Optimization**: Implemented multi-stage Docker builds to ensure lightweight, secure frontend images.
- **Professional Presence**: Rebuilt the root `README.md`, added `ARCHITECTURE.md`, and established a standard **MIT License**.
- **Developer Cockpit**: Updated the `Makefile` to provide a clean interface for `setup`, `up`, and `ingest`.

---

## 🎯 Current System Capabilities

### 🔍 Retrieval-Augmented Generation (RAG)
- **Hybrid Search**: Combines pgvector similarity with BM25 keyword matching.
- **Domain Siloing**: Automatic inference of "Department" and "Domain" from file paths.
- **Source Citations**: Every answer includes clickable citations back to the original document.

### 🤖 Agentic Intelligence
- **Multi-Step Reasoning**: Can chain multiple tool calls to solve complex queries.
- **Tool Use**: Capable of searching the web, executing scripts, and exporting professional reports.

### 📊 Quality Assurance
- **Heuristic Confidence**: Real-time scoring of answer quality based on retrieval scores.
- **Automated Evals**: Benchmarking sets included for Power BI and D365FO domains.

---

## 📜 Standard Operating Procedures (SOP)

### Starting from Scratch
1. `make setup` - Cleans environment and sets up secrets.
2. `make up` - Launches the full stack.
3. `make ingest-kb` - Scans `kb/` and populates the vector database.

### Adding New Knowledge
Drop files into `jgpt-api/kb/{domain}/{department}/`. The system will automatically detect and re-index them if `KB_WATCH=1` is enabled.

### Running Evaluations
Execute `python -m app.evals.runner` inside the `api` container to run the benchmark suite and see performance metrics.

---

## 🚀 Phase 6: Future Roadmap (The Intelligent Enterprise)
**Formalized:** 2026-02-03 00:50:58 (v0.4.0 Transition)

With the foundation solidified in Phase 5, the following high-impact enhancements are prioritized for the next stage of JGPT's evolution:

1.  **Multimodal "Vision" Integration**:
    *   Transition from image storage to image *understanding* using Ollama's `llava` model.
    *   Generate semantic descriptions for all extracted diagrams, charts, and technical assets during ingestion.
2.  **Frontend Streaming & Polish**:
    *   Implement Server-Sent Events (SSE) for real-time response streaming.
    *   Develop a "Knowledge Dashboard" for visualizing ingestion status and source health.
3.  **Hybrid Search (Vector + Keyword)**:
    *   Combine `pgvector` semantic search with traditional keyword extraction (BM25 style).
    *   Improve retrieval precision for exact technical identifiers and jargon.
4.  **Admin Management UI**:
    *   Web-based management of `sources.yaml`.
    *   Direct-to-KB file upload interface for non-technical administrators.
5.  **Multi-User & Granular Security**:
    *   JWT-based identity management.
    *   Departmental role-based access control (RBAC) to isolate sensitive knowledge.
