# Scripts

## KB Distillation (Ollama)
Generate retrieval-friendly KB cards from raw sources.

1) Put raw sources in:
- jgpt-api/kb/_sources/powerbi/
- jgpt-api/kb/_sources/d365fo/

2) Run:
```bash
python scripts/kb_distill.py --domain all
```

Outputs to:
- jgpt-api/kb/powerbi/packs/
- jgpt-api/kb/d365fo/packs/
