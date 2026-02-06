
from __future__ import annotations
import os
import sys
from datetime import datetime, timezone

# Add app to path
sys.path.append(os.path.join(os.getcwd(), "jgpt-api"))

try:
    from app.db.models import Conversation, Message
    from app.rag.embeddings import OLLAMA_EMBED_MODEL
    from app.routes.ingest import ingest_from_web
    
    print("--- Backend Verification ---")
    
    # 1. Check Embeddings Default
    print(f"Default Embedding Model: {OLLAMA_EMBED_MODEL}")
    if OLLAMA_EMBED_MODEL == "mxbai-embed-large":
        print("✅ Embeddings default aligned with models.py (1024-dim)")
    else:
        print(f"❌ Embeddings default is {OLLAMA_EMBED_MODEL}, expected mxbai-embed-large")

    # 2. Check models.py defaults
    # We inspect the column default
    conv_created_at_default = Conversation.__table__.columns['created_at'].default
    msg_created_at_default = Message.__table__.columns['created_at'].default
    
    print(f"Conversation created_at default: {conv_created_at_default}")
    if hasattr(conv_created_at_default, 'arg') and callable(conv_created_at_default.arg):
         print("✅ models.py uses callable (lambda) for created_at default")
    else:
         print("❌ models.py might still be using static value or utcnow")

    # 3. Check imports in ingest.py
    import app.routes.ingest as ingest_mod
    if hasattr(ingest_mod, 'timezone'):
        print("✅ ingest.py has timezone imported")
    else:
        print("❌ ingest.py missing timezone import")

except Exception as e:
    print(f"Verification Error: {e}")
    import traceback
    traceback.print_exc()
