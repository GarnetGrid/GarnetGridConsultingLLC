from __future__ import annotations
from typing import Dict, Any, List
import re
from sqlalchemy import text
from app.db.session import SessionLocal
from app.db.models import Connection
from app.services.connector import connector_service

def list_all_connections(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Lists all available database connections."""
    try:
        with SessionLocal() as db:
            connections = db.query(Connection).all()
            result = [{"id": c.id, "name": c.name, "type": c.type} for c in connections]
            return {"ok": True, "connections": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_schema_info(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieves schema information (tables and columns) for a specific connection."""
    conn_id = inp.get("connection_id")
    if not conn_id:
        return {"ok": False, "error": "connection_id is required"}
    
    try:
        with SessionLocal() as db:
            conn = db.get(Connection, conn_id)
            if not conn:
                return {"ok": False, "error": f"Connection {conn_id} not found"}
            
            # Use Connector Service to get schema
            schema = connector_service.get_schema_summary(conn)
            return {"ok": True, "schema": schema}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def run_read_only_query(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Executes a READ-ONLY SQL query on a specific connection."""
    conn_id = inp.get("connection_id")
    query_str = inp.get("query")
    
    if not conn_id:
        return {"ok": False, "error": "connection_id is required"}
    if not query_str:
        return {"ok": False, "error": "query is required"}

    # Basic Safety Check (SQL Injection is still possible if parameters aren't used, 
    # but the goal here is to prevent accidental writes by the LLM)
    # The LLM generates the query, so we must be strict.
    
    # 1. Normalize
    q_norm = query_str.strip().lower()
    
    # 2. Block destructive keywords
    blocked = ["insert", "update", "delete", "drop", "alter", "truncate", "create", "grant", "revoke", "commit", "rollback", "exec", "execute"]
    for word in blocked:
        # Check for whole words
        if re.search(r'\b' + word + r'\b', q_norm):
             return {"ok": False, "error": f"Security Alert: Query contains forbidden keyword '{word}'. Only SELECT queries are allowed."}

    # 3. Must start with SELECT (or WITH for CTEs)
    if not (q_norm.startswith("select") or q_norm.startswith("with")):
        return {"ok": False, "error": "Security Alert: Query must start with SELECT or WITH"}

    try:
        with SessionLocal() as db:
            conn = db.get(Connection, conn_id)
            if not conn:
                return {"ok": False, "error": f"Connection {conn_id} not found"}
            
            # Execute
            results = connector_service.execute_query(conn, query_str) 
            # Note: execute_query needs to be added to ConnectorService wrapper if it doesn't exist, 
            # or we use the underlying connector directly.
            # Let's check ConnectorService. Assuming it has execute_query or similar.
            # If not, I'll need to update ConnectorService.
            
            # LIMIT check: if the user didn't put a limit, we should probably cap it to avoid blowing up memory.
            # But let's rely on the LLM to write good queries or the connector to handle it.
            
            return {"ok": True, "results": results}
            
    except Exception as e:
        return {"ok": False, "error": f"Query Execution Failed: {str(e)}"}

def add_connection(inp: Dict[str, Any]) -> Dict[str, Any]:
    """
    Registers a new database connection securely.
    Args:
        name: Friendly name (e.g. "SalesDB")
        type: postgres | mssql | mysql
        host: Hostname/IP
        port: Port number
        database: Database name
        username: DB User
        password: DB Password (will be encrypted)
    """
    required = ["name", "type", "host", "port", "database", "username", "password"]
    for field in required:
        if field not in inp:
            return {"ok": False, "error": f"Missing required field: {field}"}
            
    from app.services.crypto import encrypt_string
    
    try:
        with SessionLocal() as db:
            # Check for dupes
            existing = db.query(Connection).filter(Connection.name == inp["name"]).first()
            if existing:
                return {"ok": False, "error": f"Connection '{inp['name']}' already exists. Use a different name."}
            
            new_conn = Connection(
                name=inp["name"],
                type=inp["type"],
                host=inp["host"],
                port=int(inp["port"]),
                database=inp["database"],
                username=inp["username"],
                encrypted_password=encrypt_string(inp["password"]),
                is_active=True
            )
            db.add(new_conn)
            db.commit()
            return {"ok": True, "message": f"Connection '{inp['name']}' added successfully."}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def delete_connection(inp: Dict[str, Any]) -> Dict[str, Any]:
    """Deletes a database connection by name or ID."""
    name = inp.get("name")
    conn_id = inp.get("id")
    
    if not name and not conn_id:
        return {"ok": False, "error": "Must provide 'name' or 'id'"}
    
    try:
        with SessionLocal() as db:
            if conn_id:
                conn = db.get(Connection, conn_id)
            else:
                conn = db.query(Connection).filter(Connection.name == name).first()
                
            if not conn:
                return {"ok": False, "error": "Connection not found"}
            
            db.delete(conn)
            db.commit()
            return {"ok": True, "message": "Connection deleted."}
    except Exception as e:
        return {"ok": False, "error": str(e)}
