from sqlalchemy import text
from app.db.session import SessionLocal

def upgrade():
    print("Upgrading database schema...")
    with SessionLocal() as db:
        try:
            # check if column exists
            result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='messages' AND column_name='embedding'"))
            if result.fetchone():
                print("Column 'embedding' already exists in 'messages'.")
            else:
                print("Adding 'embedding' column to 'messages'...")
                db.execute(text("ALTER TABLE messages ADD COLUMN embedding vector(1024)"))
                db.execute(text("CREATE INDEX ix_messages_embedding ON messages USING hnsw (embedding vector_cosine_ops)"))
                db.commit()
                print("Column added successfully.")
        except Exception as e:
            print(f"Error upgrading database: {e}")
            db.rollback()

if __name__ == "__main__":
    upgrade()
