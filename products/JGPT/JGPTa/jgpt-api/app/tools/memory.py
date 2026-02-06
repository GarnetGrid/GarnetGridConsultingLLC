from typing import Dict, Any
from app.db.session import get_db
from app.services.context_service import ContextService
from app.util.auth import get_current_user # Dependency simulation

# NOTE: In the actual tool runtime, we need a way to get the current user ID.
# For now, we will assume the tool is called within a context where 'user_id' is passed 
# or we'll default to a system user if not available (to be refined in verify_tools).

def remember_fact(key: str, value: str, user_id: int = 1):
    """
    Saves a fact to your long-term memory. 
    Use this when the user tells you a preference, project detail, or specific instruction 
    that you should remember for the future.
    
    Args:
        key: The category or label (e.g., "user_preference", "project_falcon").
        value: The detail to remember (e.g., "prefers dark mode", "deadline is Q4").
        user_id: The ID of the user (injected by system, do not guess).
    """
    db = next(get_db())
    svc = ContextService(db)
    svc.set_context_fact(user_id, key, value)
    return f"I have committed this to memory: [{key}] = {value}"

def remember_entity(name: str, type: str, description: str, user_id: int = 1):
    """
    Registers a specific entity (Project, Server, Person) in memory.
    
    Args:
        name: The name of the entity (e.g., "Server-01", "Project Phoenix").
        type: The type (e.g., "server", "project", "person").
        description: A brief summary of what this entity is.
        user_id: The ID of the user (injected by system).
    """
    db = next(get_db())
    svc = ContextService(db)
    svc.remember_entity(user_id, name, type, description)
    return f"I have registered the entity '{name}' ({type}) in my database."

def list_facts(inp: Dict[str, Any], user_id: int = 1) -> Dict[str, Any]:
    """Lists all facts currently stored in memory for the user."""
    db = next(get_db())
    svc = ContextService(db)
    # ContextService needs a method to return raw list with IDs for deletion
    # For now, we will use the existing get_user_context but ideally we want IDs.
    # Let's check ContextService.get_user_context. It returns a dict {key: value}.
    # We need a new method in ContextService or access DB directly here.
    # Direct DB access is faster for this tool.
    from app.db.models import PrimedContext
    from sqlalchemy import select
    
    stm = select(PrimedContext).where(PrimedContext.user_id == user_id)
    results = db.scalars(stm).all()
    
    facts = [{"id": r.id, "key": r.context_type, "value": r.context_data} for r in results]
    return {"facts": facts}

def delete_fact(inp: Dict[str, Any], user_id: int = 1) -> Dict[str, Any]:
    """Deletes a specific fact from memory by ID."""
    fact_id = inp.get("id")
    if not fact_id:
        return {"error": "fact_id is required"}
        
    db = next(get_db())
    from app.db.models import PrimedContext
    
    fact = db.get(PrimedContext, fact_id)
    if not fact:
        return {"error": "Fact not found"}
        
    # Security check: ensure it belongs to user
    if fact.user_id != user_id:
        return {"error": "Unauthorized"}
        
    db.delete(fact)
    db.commit()
    return {"message": f"Deleted fact ID {fact_id}"}
