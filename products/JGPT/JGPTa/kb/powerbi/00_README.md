# Power BI Knowledge Base (KB)

This folder is designed for Retrieval-Augmented Generation (RAG). Files here are ingested, chunked, embedded, and stored in Postgres/pgvector.

## Authoring rules (so retrieval works well)
- Prefer short “pattern cards” over long essays.
- Use headings and bullet lists.
- Include copy/paste-ready code blocks.
- Include “Common mistakes” and “Variants”.

## Suggested file types
- .md (preferred)
- .txt

## After editing KB
Re-run ingestion so the new content is embedded and searchable.
