# Power BI Knowledge Base (KB)

This folder is ingested into Postgres/pgvector for Retrieval-Augmented Generation (RAG).

## Authoring rules (so retrieval works well)
- Prefer short “pattern cards” over long essays.
- Use headings and bullet lists.
- Include copy/paste-ready code blocks.
- Include “Common mistakes” and “Variants”.

## After editing KB
- Call `POST /ingest/kb` (no API restart needed)
- Verify citations reference these files
