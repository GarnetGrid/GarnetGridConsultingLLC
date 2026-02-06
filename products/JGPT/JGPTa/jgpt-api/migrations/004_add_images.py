"""
Database migration: Add images and chunk_images tables for multi-modal support.
"""

sql = """
-- Create images table
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL UNIQUE,
    mime_type TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    description TEXT,
    embedding vector(1024),
    source_url TEXT,
    source_page INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create chunk_images junction table
CREATE TABLE IF NOT EXISTS chunk_images (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    image_id INTEGER NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_images_embedding ON images USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_chunk_images_chunk_id ON chunk_images(chunk_id);
CREATE INDEX IF NOT EXISTS idx_chunk_images_image_id ON chunk_images(image_id);

-- Prevent duplicate chunk-image associations
CREATE UNIQUE INDEX IF NOT EXISTS idx_chunk_images_unique ON chunk_images(chunk_id, image_id);
"""

if __name__ == "__main__":
    import os
    import psycopg
    from dotenv import load_dotenv
    
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    
    # Convert SQLAlchemy URL to psycopg format
    if db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://")
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    
    print("✅ Migration completed: Added images and chunk_images tables")
