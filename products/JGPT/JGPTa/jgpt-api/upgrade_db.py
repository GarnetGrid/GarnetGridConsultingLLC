from sqlalchemy import text
from app.db.session import SessionLocal

def upgrade():
    print("Upgrading database schema...")
    with SessionLocal() as db:
        # 1. Embedding column on messages
        try:
            result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='messages' AND column_name='embedding'"))
            if not result.fetchone():
                print("Adding 'embedding' column to 'messages'...")
                db.execute(text("ALTER TABLE messages ADD COLUMN embedding vector(1024)"))
                db.execute(text("CREATE INDEX ix_messages_embedding ON messages USING hnsw (embedding vector_cosine_ops)"))
                db.commit()
                print("Added embedding column.")
            else:
                print("Embedding column already exists.")
        except Exception as e:
            print(f"Error with embedding column: {e}")
            db.rollback()

        # 2. client_id columns
        tables = ["documents", "chunks", "conversations", "api_keys"]
        for table in tables:
            try:
                # Check if table exists first (api_keys might not exist if new)
                # But here we assume tables exist or errors will verify.
                # Actually checking column existence is safer.
                res = db.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND column_name='client_id'"))
                if not res.fetchone():
                    print(f"Adding 'client_id' to '{table}'...")
                    db.execute(text(f"ALTER TABLE {table} ADD COLUMN client_id text DEFAULT 'default' NOT NULL"))
                    db.execute(text(f"CREATE INDEX ix_{table}_client_id ON {table} (client_id)"))
                    db.commit()
                    print(f"Added client_id to {table}.")
                else:
                    print(f"client_id already in {table}.")
            except Exception as e:
                print(f"Error adding client_id to {table}: {e}")
                db.rollback()

        # 3. Create IngestionJob table if not exists
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS ingestion_jobs (
                    id SERIAL PRIMARY KEY,
                    client_id TEXT NOT NULL DEFAULT 'default',
                    status TEXT NOT NULL DEFAULT 'pending',
                    source_type TEXT NOT NULL,
                    source_target TEXT NOT NULL,
                    error TEXT,
                    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() at time zone 'utc'),
                    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (now() at time zone 'utc')
                );
                CREATE INDEX IF NOT EXISTS ix_ingestion_jobs_client_id ON ingestion_jobs (client_id);
                CREATE INDEX IF NOT EXISTS ix_ingestion_jobs_status ON ingestion_jobs (status);
            """))
            db.commit()
            print("Created ingestion_jobs table.")
        except Exception as e:
            print(f"Error creating ingestion_jobs table: {e}")
            db.rollback()

if __name__ == "__main__":
    upgrade()
