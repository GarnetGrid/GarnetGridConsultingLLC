# JGPT Demo Script (5–7 minutes)

## What it is
A local Copilot platform for **Power BI** + **D365 F&O (X++)**:
- RAG grounded on a repo-tracked KB (**md/pdf/docx**)
- Postgres + **pgvector** retrieval + **MMR**
- Deterministic tools for templates/checklists/snippets
- Conversation persistence
- Eval harness + **LLM-judge** output (markdown + json)

## Live demo flow
1) **Open UI**: http://localhost:3000
2) Ask (Power BI):
   - “Why does a measure work in a card but not a matrix?”
   - Point out **citations** + **tool trace**
3) Ask (Power BI time-intelligence):
   - “Week 48 selected but last week sales is blank—fix trailing weeks”
4) Switch mode to **D365 F&O**:
   - “Explain ttsBegin/ttsCommit nesting and what happens on exception”
5) Trigger incremental ingest live:
   - `curl -X POST http://localhost:8000/ingest/kb`
6) Run eval suite:
   - `python3 scripts/run_eval.py`
   - Show **report_*.md** + **report_*.json**

## Engineering highlights to mention
- Split repos (infra/api/web) + Docker Compose
- Incremental ingest (hashing) + pgvector similarity search
- **IVFFLAT** index for scale (plus ANALYZE)
- MMR to reduce duplicate chunks in retrieval
- CI + integration tests


## New polish
- UI toggles: short/deep, citations, tool trace
- Retrieval timing shown
- DAX Guard auto-warnings
- Evals tab (run + load latest report)
