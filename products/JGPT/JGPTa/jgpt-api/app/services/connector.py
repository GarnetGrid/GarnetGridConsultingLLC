from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from app.db.models import Connection
from app.services.crypto import decrypt_string
import urllib.parse

class ConnectorService:
    def get_connection_url(self, conn: Connection) -> str:
        password = decrypt_string(conn.encrypted_password)
        encoded_password = urllib.parse.quote_plus(password)
        
        if conn.type == "postgres":
            return f"postgresql+psycopg2://{conn.username}:{encoded_password}@{conn.host}:{conn.port}/{conn.database}"
        elif conn.type == "mssql":
            # Using pymssql for simple linux compatibility
            return f"mssql+pymssql://{conn.username}:{encoded_password}@{conn.host}:{conn.port}/{conn.database}"
        elif conn.type == "mysql":
            return f"mysql+pymysql://{conn.username}:{encoded_password}@{conn.host}:{conn.port}/{conn.database}"
        else:
            raise ValueError(f"Unsupported connection type: {conn.type}")

    def get_engine(self, conn: Connection):
        url = self.get_connection_url(conn)
        return create_engine(url, echo=False)

    def test_connection(self, conn: Connection) -> bool:
        try:
            engine = self.get_engine(conn)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            raise e

    def get_schema_summary(self, conn: Connection) -> dict:
        """Returns a summary of tables and columns for the Agent."""
        engine = self.get_engine(conn)
        inspector = inspect(engine)
        
        summary = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_list = [f"{col['name']} ({col['type']})" for col in columns]
            summary[table_name] = col_list
            
        return summary
    
    def execute_query(self, conn: Connection, query: str) -> list[dict]:
        """Executes a raw SQL query and returns results as a list of dicts."""
        engine = self.get_engine(conn)
        with engine.connect() as connection:
            result = connection.execute(text(query))
            # Convert to list of dicts
            return [dict(row._mapping) for row in result]
    
connector_service = ConnectorService()
