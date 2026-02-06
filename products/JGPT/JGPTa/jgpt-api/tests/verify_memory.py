import sys
import os

# Create a mock environment to run this script standalone
sys.path.append(os.getcwd())

from app.db.session import SessionLocal, engine
from app.db.models import Base
from app.services.context_service import ContextService
from app.tools import memory

def verify_memory():
    print("🧠 Verifying Memory System...")
    
    # 1. Setup DB Session
    db = SessionLocal()
    
    # Ensure tables exist (in case migration didn't run via main app yet)
    # Base.metadata.create_all(bind=engine) 
    # ^ We rely on the main app having initialized it, or we do it here if needed.
    # Let's try to trust the restart first.
    
    # 2. Get a valid user
    from app.db.models import User
    user = db.query(User).first()
    if not user:
        print("   ⚠️ No user found. Creating test user...")
        user = User(email="test_me@jgpt.com", hashed_password="pw", role="viewer")
        db.add(user)
        db.commit()
    
    user_id = user.id
    print(f"   ✅ Using User ID: {user_id}")
    
    try:
        # 2. Test remember_fact
        print(f"🔹 Testing remember_fact for user {user_id}...")
        res = memory.remember_fact("test_preference", "dark_mode_enabled", user_id=user_id)
        print(f"   Tool Output: {res}")
        
        # Verify via Service
        svc = ContextService(db)
        ctx = svc.get_user_context(user_id)
        assert ctx.get("test_preference") == "dark_mode_enabled"
        print("   ✅ Fact verification passed.")

        # 3. Test remember_entity
        print(f"🔹 Testing remember_entity for user {user_id}...")
        res_ent = memory.remember_entity("Project Omega", "project", "Doomsday Device", user_id=user_id)
        print(f"   Tool Output: {res_ent}")
        
        # Verify via Service
        entities = svc.get_all_entities(user_id)
        target = next((e for e in entities if e["name"] == "Project Omega"), None)
        assert target is not None
        assert target["type"] == "project"
        assert target["description"] == "Doomsday Device"
        print("   ✅ Entity verification passed.")
        
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    verify_memory()
