# JGPT API

The intelligent backend for the Garnet Grid AI Engine. 
A RAG-powered expert system specializing in **Microsoft D365 Finance & Operations** and **Power BI**.

## 🚀 Key Features
- **Senior Developer Personas**: Enforced system prompts for "Solution Architect" level outputs (Performance, Security, Best Practices).
- **Hybrid PDF Ingestion**: Automatically detects image-heavy slides and uses **Local OCR** (Tesseract) to extract hidden text.
- **Incremental RAG**: Vector-based retrieval using `pgvector` and `mxbai-embed-large`.
- **Evals Framework**: Built-in LLM-judge for verifying answer quality.

## 🛠️ Prerequisites
### System Tools (Required for OCR)
You must install these for PDF image extraction to work:
```bash
brew install tesseract poppler
```

### AI Models (Ollama)
```bash
ollama serve
ollama pull llama3.2
ollama pull mxbai-embed-large
```

## ⚡ Quick Start

### 1. Start Infrastructure
```bash
cd ../jgpt-infra
docker compose up --build
```

### 2. Install Python Dependencies
```bash
cd ../jgpt-api
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 3. Ingest Knowledge Base
Ingest local markdown guides + web sources (SQLBI, MS Learn):
```bash
# Ingest local KB (X++ Patterns, DAX Context, etc.)
python scripts/ingest_kb.py

# Ingest curted web sources (defined in scripts/sources.yaml)
python scripts/ingest_web.py
```

## 🧠 Copilot Specializations

### D365FO / X++ Architect
- Focuses on **Performance** (`insert_recordset`, `update_recordset`).
- Enforces **Chain of Command (CoC)** over event handlers.
- Understands **SysOperationFramework** and Batch bundling.

### Power BI / DAX Pro
- Enforces **Star Schema** modeling.
- Automatic **Context Transition** handling in measures.
- Blocks usage of "Implicit Measures".

## 🧪 Testing
```bash
# Health Check
curl http://localhost:8001/health

# Test Chat
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"mode":"powerbi","message":"How do I optimize a many-to-many relationship?"}'

### Verified Live Demo
To run a full system demonstration in the terminal:
```bash
pythontests/live_demo.py
```
```
