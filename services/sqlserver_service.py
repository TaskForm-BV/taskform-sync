import pyodbc
from typing import List, Dict, Any, Optional
from utils.logging import Logger

class SQLServerService:
    """Service for SQL Server database operations."""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.logger = Logger("sqlserver")
    
    def test_connection(self) -> bool:
        """Test SQL Server connection."""
        try:
            conn = pyodbc.connect(self.connection_string, timeout=5)
            conn.close()
            self.logger.success("SQL Server connection successful")
            return True
        except Exception as e:
            self.logger.error("SQL Server connection failed", e)
            raise Exception(f"SQL Server connection failed: {str(e)}")
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dictionaries."""
        try:
            self.logger.info(f"Executing SQL Server query")
            
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            cursor.execute(sql)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows and convert to list of dictionaries
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            conn.close()
            
            self.logger.success(f"SQL Server query executed successfully, {len(results)} rows returned")
            return results
            
        except Exception as e:
            self.logger.error("SQL Server query execution failed", e)
            raise Exception(f"SQL Server query failed: {str(e)}")
    
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