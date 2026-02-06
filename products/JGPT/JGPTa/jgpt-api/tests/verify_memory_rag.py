import asyncio
import sys
import os

# Ensure logic is importable
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.models import Message, User
from app.tools.memory_search import search_history
from app.routes.chat import update_message_embedding

# Mock embed_one to avoid huge downloads if not present, 
# BUT we want to verify real integration if possible. 
# If OLLAMA is required, we assume it's running.
# However, to avoid dependency on real embedding model for a quick test, 
# we can mock it IF we just want to test wiring.
# But the user asked for "Advanced Long-term Memory", so we should test with real embeddings if possible.
# Given the environment ("testing or doing demo"), we assume services are up.

async def verify_rag():
    print("Verifying Memory RAG...")
    
    # 1. Create a message manually
    with SessionLocal() as db:
        # cleanup old test messages
        db.query(Message).filter(Message.content.like("VERIFY_RAG_TEST:%")).delete()
        db.commit()
        
        # Verify user exists (ID 1)
        user = db.get(User, 1)
        if not user:
             print("Creating test user...")
             from app.services.auth import get_password_hash
             user = User(email="test@monitor.com", hashed_password=get_password_hash("secret"), role="admin")
             db.add(user)
             db.commit()

        # Create message
        msg = Message(role="user", content="VERIFY_RAG_TEST: The code for the Falcon project is in /var/www/falcon.")
        # Need a conversation?
        from app.db.models import Conversation
        conv = Conversation(user_id=1, title="Test RAG", mode="test")
        db.add(conv)
        db.commit()
        
        msg.conversation_id = conv.id
        db.add(msg)
        db.commit()
        msg_id = msg.id
        print(f"Created test message ID: {msg_id}")

    # 2. Embed it (using real embedding logic from update_message_embedding)
    # We will simulate the async update
    print("Generating embedding for message...")
    from app.rag.embeddings import embed_one
    emb = await embed_one("The code for the Falcon project is in /var/www/falcon.")
    
    print("Updating message embedding...")
    update_message_embedding(msg_id, emb)
    
    # 3. Search for it
    print("Searching for 'falcon code location'...")
    res = await search_history({"query": "where is the falcon project code?", "limit": 3})
    
    if not res["ok"]:
        print(f"Search failed: {res['error']}")
        return
        
    found = False
    for hit in res["results"]:
        print(f"Hit: {hit['content']} (ID: {hit['id']})")
        if "VERIFY_RAG_TEST" in hit["content"]:
            found = True
            
    if found:
        print("SUCCESS: Retrieved specific memory via semantic search.")
    else:
        print("FAILURE: Did not find the test message in top results.")

if __name__ == "__main__":
    asyncio.run(verify_rag())
