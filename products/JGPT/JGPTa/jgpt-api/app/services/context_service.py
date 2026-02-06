from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.db.models import PrimedContext, ContextEntity
import json

class ContextService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_context(self, user_id: int) -> dict:
        """Retrieves user's holistic context as a dictionary."""
        # 1. Get raw key-value store (PrimedContext)
        # Note: In the revamped model, we effectively treat PrimedContext rows as KV pairs
        # or we might iterate over them. For now, assuming PrimedContext stores JSON blobs.
        # Let's align with the model: context_type is the "KEY", context_data is the "VALUE"
        
        stm = select(PrimedContext).where(PrimedContext.user_id == user_id)
        results = self.db.scalars(stm).all()
        
        context = {}
        for row in results:
            try:
                # Try parsing as JSON, fallback to string
                context[row.context_type] = json.loads(row.context_data)
            except:
                context[row.context_type] = row.context_data
                
        return context

    def set_context_fact(self, user_id: int, key: str, value: any):
        """Sets a specific fact (Key-Value) for the user."""
        stmt = select(PrimedContext).where(
            PrimedContext.user_id == user_id, 
            PrimedContext.context_type == key
        )
        existing = self.db.scalar(stmt)
        
        val_str = json.dumps(value) if not isinstance(value, str) else value
        
        if existing:
            existing.context_data = val_str
        else:
            new_ctx = PrimedContext(
                user_id=user_id,
                context_type=key,
                context_data=val_str
            )
            self.db.add(new_ctx)
        
        self.db.commit()

    def remember_entity(self, user_id: int, name: str, type: str, description: str):
        """Remembers a specific named entity (Project, Server, Client)."""
        stmt = select(ContextEntity).where(
            ContextEntity.user_id == user_id,
            ContextEntity.name == name
        )
        existing = self.db.scalar(stmt)
        
        if existing:
            existing.entity_type = type
            existing.description = description
        else:
            new_ent = ContextEntity(
                user_id=user_id,
                name=name,
                entity_type=type,
                description=description
            )
            self.db.add(new_ent)
        
        self.db.commit()

    def get_all_entities(self, user_id: int) -> list[dict]:
        stmt = select(ContextEntity).where(ContextEntity.user_id == user_id)
        rows = self.db.scalars(stmt).all()
        return [
            {"name": r.name, "type": r.entity_type, "description": r.description} 
            for r in rows
        ]
