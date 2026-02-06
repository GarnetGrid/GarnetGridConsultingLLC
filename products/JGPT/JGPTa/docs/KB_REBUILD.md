# JGPT Knowledge Base Rebuild Guide

This document explains **how to fully rebuild and expand the JGPT Knowledge Base** using the automated pipeline.

It covers:
- Ollama-powered KB distillation
- Local KB ingestion
- Optional web ingestion
- One-command rebuild workflow

---

## Prerequisites

### Local script dependencies (Mac/Linux)
```bash
./scripts/install_local_deps.sh
```

Or manually:
```bash
python3 -m pip install -r scripts/requirements.txt
```


### Services running
```bash
docker compose up -d
```

Verify:
```bash
curl http://localhost:8000/health
```

### Ollama models available
```bash
ollama list
ollama pull llama3.2
ollama pull nomic-embed-text
```

---

## Folder Structure

```
jgpt-api/kb/
├── _sources/              # RAW source material (docs, notes, exports)
│   ├── powerbi/
│   └── d365fo/
├── powerbi/
│   └── packs/             # Generated pattern cards (ingested)
├── d365fo/
│   └── packs/             # Generated pattern cards (ingested)
```

---

## One-Command Rebuild (Recommended)

```bash
./scripts/rebuild_kb.sh
```

This will:
1. Wait for API health
2. Distill KB pattern cards using Ollama
3. Ingest repo KB (`POST /ingest/kb`)
4. Finish with a clean, expanded vector store

---

## Rebuild Options

### Skip distillation (ingest only)
```bash
DO_DISTILL=0 ./scripts/rebuild_kb.sh
```

### Only distill Power BI
```bash
DISTILL_DOMAIN=powerbi ./scripts/rebuild_kb.sh
```

### Include curated web ingestion
```bash
DO_WEB=1 WEB_FORCE=1 WEB_MAX_PAGES=25 ./scripts/rebuild_kb.sh
```

---

## Manual Steps (If Needed)

### 1. Distill KB from sources
```bash
python3 scripts/kb_distill.py --domain all
```

### 2. Ingest KB
```bash
curl -X POST http://localhost:8000/ingest/kb
```

### 3. Ingest curated web sources
```bash
curl -X POST "http://localhost:8000/ingest/web?force=true&max_pages=25"
```

---

## Verification Checklist

Ask in the UI:
> Create a DateTable using fact-table min/max dates

Confirm:
- Citations reference `kb/*/packs/*.md`
- Tool trace shows `rag.retrieve`
- Confidence score increases (if `grade=true`)

---

## Troubleshooting

### Embeddings failing
```bash
ollama pull nomic-embed-text
```

### Empty citations
- Ensure files are under `jgpt-api/kb/`
- Re-run ingest

### API ingest errors
Check logs:
```bash
docker compose logs api
```

---

## Best Practices

- Prefer many **small pattern cards** over large docs
- Always distill raw sources before ingesting
- Add eval questions after major KB expansions
- Version KB changes in `kb/*/VERSION.md`

---

**JGPT KB Rebuild = Deterministic, Local, and Scalable**


## Auto-venv behavior

`./scripts/rebuild_kb.sh` will auto-create and activate `.venv/` and install `scripts/requirements.txt` as needed.
