from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User, Connection
from app.util.auth import get_current_admin, get_db
from app.services.connector import connector_service
from app.services.crypto import encrypt_string
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# --- Schemas ---

class ConnectionCreate(BaseModel):
    name: str
    type: str # postgres, mssql, mysql
    host: str
    port: int
    database: str
    username: str
    password: str

class ConnectionResponse(BaseModel):
    id: int
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        orm_mode = True

class SchemaResponse(BaseModel):
    tables: dict # table_name -> [col1, col2]

# --- Endpoints ---

@router.post("/", response_model=ConnectionResponse)
def create_connection(conn_in: ConnectionCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    # Encrypt password
    encrypted = encrypt_string(conn_in.password)
    
    new_conn = Connection(
        name=conn_in.name,
        type=conn_in.type,
        host=conn_in.host,
        port=conn_in.port,
        database=conn_in.database,
        username=conn_in.username,
        encrypted_password=encrypted,
        is_active=True
    )
    
    db.add(new_conn)
    db.commit()
    db.refresh(new_conn)
    
    # Return response (Pydantic will strip encrypted_password as it's not in schema)
    return {
        "id": new_conn.id,
        "name": new_conn.name,
        "type": new_conn.type,
        "host": new_conn.host,
        "port": new_conn.port,
        "database": new_conn.database,
        "username": new_conn.username,
        "is_active": new_conn.is_active,
        "created_at": new_conn.created_at.isoformat()
    }

@router.get("/")
def list_connections(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        conns = db.query(Connection).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "host": c.host,
                "port": c.port,
                "database": c.database,
                "username": c.username,
                "is_active": c.is_active,
                "created_at": c.created_at
            }
            for c in conns
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")

@router.post("/{conn_id}/test")
def test_connection_endpoint(conn_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    conn = db.query(Connection).filter(Connection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    try:
        success = connector_service.test_connection(conn)
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.get("/{conn_id}/schema", response_model=SchemaResponse)
def get_connection_schema(conn_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    conn = db.query(Connection).filter(Connection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
        
    try:
        summary = connector_service.get_schema_summary(conn)
        return {"tables": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Schema fetch failed: {str(e)}")

@router.delete("/{conn_id}")
def delete_connection(conn_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    conn = db.query(Connection).filter(Connection.id == conn_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(conn)
    db.commit()
    return {"message": "Connection deleted"}
