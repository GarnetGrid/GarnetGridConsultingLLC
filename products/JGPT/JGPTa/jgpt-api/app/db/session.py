from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return create_engine(url, pool_pre_ping=True)

engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
