import fdb
from typing import List, Dict, Any, Optional
from utils.logging import Logger

class FirebirdService:
    """Service for Firebird database operations."""
    
    def __init__(self, database_path: str, username: str, password: str):
        self.database_path = database_path
        self.username = username
        self.password = password
        self.logger = Logger("firebird")
    
    def test_connection(self) -> bool:
        """Test Firebird connection."""
        try:
            conn = fdb.connect(
                dsn=self.database_path,
                user=self.username,
                password=self.password
            )
            conn.close()
            self.logger.success("Firebird connection successful")
            return True
        except Exception as e:
            self.logger.error("Firebird connection failed", e)
            raise Exception(f"Firebird connection failed: {str(e)}")
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dictionaries."""
        try:
            self.logger.info(f"Executing Firebird query")
            
            conn = fdb.connect(
                dsn=self.database_path,
                user=self.username,
                password=self.password
            )
            cursor = conn.cursor()
            
            cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows and convert to list of dictionaries
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            conn.close()
            
            self.logger.success(f"Firebird query executed successfully, {len(results)} rows returned")
            return results
            
        except Exception as e:
            self.logger.error("Firebird query execution failed", e)
            raise Exception(f"Firebird query failed: {str(e)}")
    
    def execute_query_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Execute SQL query from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            self.logger.info(f"Executing query from file: {file_path}")
            return self.execute_query(sql)
            
        except Exception as e:
            self.logger.error(f"Failed to execute query from file: {file_path}", e)
            raise