CREATE EXTENSION IF NOT EXISTS vector;

-- Vector index for faster similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_cosine
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

ANALYZE;
