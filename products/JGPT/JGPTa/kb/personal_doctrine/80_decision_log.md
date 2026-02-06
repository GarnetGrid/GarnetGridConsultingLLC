## DEC-2026-02-01: Reduce chunk size to 300 chars

- **Context:** Embedding crashes on large documentation pages
- **Decision:** Use 300-character chunks with recursive splitting
- **Why:** Stability and ingestion reliability outweigh semantic purity
- **Impact:** Higher vector count, higher cost, zero crashes
- **Tags:** #ingestion #embeddings
