# 🚀 JGPT: Enterprise-Grade Agentic RAG

JGPT is a powerful, production-ready Retrieval-Augmented Generation (RAG) system built for teams that demand privacy, performance, and agentic intelligence.

![Version](https://img.shields.io/badge/version-0.3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Key Features

- 🧠 **Agentic Reasoning**: Multi-step problem solving with built-in tool use.
- 👁️ **Multimodal Vision**: Understands and captions images within your documents using LLaVA.
- 🎯 **Hybrid Search**: Advanced RRF-based fusion of Vector and Keyword search for maximum precision.
- 📈 **Knowledge Dashboard**: Real-time stats and management for your knowledge base.
- 🔒 **Privacy First**: Fully compatible with local LLMs via Ollama.
- 🏢 **Enterprise Ready**: Department-aware retrieval and robust metadata filtering.
- 📊 **Truth Audit**: Fact-checking with confidence scoring and source citations.
- 📄 **Pro Export**: Generate professional Markdown reports from chat results.

## 🏗️ Architecture

JGPT is composed of three primary services:
1.  **Next.js Frontend**: A sleek, high-performance UI for chat and KB management.
2.  **FastAPI Backend**: The core RAG engine and agentic brain.
3.  **pgvector DB**: High-performance vector storage for lightning-fast retrieval.

Read more in [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- [Ollama](https://ollama.com/) (running on host)

### 1. Initialize
```bash
make setup
```

### 2. Launch Stack
```bash
make up
```
Open [http://localhost:3001](http://localhost:3001) to start chatting.
**Default Credentials:** `admin@jgpt.com` / `admin`

### 3. Ingest Knowledge
```bash
make ingest-kb
```

## 🛠️ Configuration
Configure the system via the `.env` file created during setup.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `API_KEY` | Security key for API access | `jgpt_master_key` |
| `OLLAMA_BASE_URL` | Endpoint for local LLM | `http://host.docker.internal:11434` |
| `POSTGRES_DB` | Database name | `jgpt` |
| `BACKEND_PORT` | API Service Port | `8001` |
| `FRONTEND_PORT` | Web Service Port | `3001` |

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.
