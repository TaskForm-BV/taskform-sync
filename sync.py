import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from config import Config
from services.sqlserver_service import SQLServerService
from services.firebird_service import FirebirdService
from services.api_service import APIService
from utils.logging import Logger

class SyncService:
    """Main sync service for DataSync application."""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger("sync")
        
        # Initialize services
        self.sql_service = None
        self.fb_service = None
        self.api_service = None
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize database and API services based on configuration."""
        # Initialize SQL Server if enabled
        if self.config.is_sql_server_enabled():
            sql_config = self.config.get_sql_server_config()
            if sql_config.get("connection_string"):
                self.sql_service = SQLServerService(sql_config["connection_string"])
                self.logger.info("SQL Server service initialized")
        
        # Initialize Firebird if enabled
        if self.config.is_firebird_enabled():
            fb_config = self.config.get_firebird_config()
            if all([fb_config.get("database_path"), fb_config.get("username"), fb_config.get("password")]):
                self.fb_service = FirebirdService(
                    fb_config["database_path"],
                    fb_config["username"],
                    fb_config["password"]
                )
                self.logger.info("Firebird service initialized")
        
        # Initialize API service
        api_config = self.config.get_api_config()
        if all([api_config.get("base_url"), api_config.get("api_key"), api_config.get("tenant_id")]):
            self.api_service = APIService(
                api_config["base_url"],
                api_config["api_key"],
                api_config["tenant_id"]
            )
            self.logger.info("API service initialized")
        else:
            raise Exception("API configuration is incomplete")
    
    def get_query_files(self) -> List[str]:
        """Get all SQL query files from queries folder."""
        sync_config = self.config.get_sync_config()
        queries_folder = sync_config.get("queries_folder", "queries")
        
        if not os.path.exists(queries_folder):
            self.logger.warning(f"Queries folder not found: {queries_folder}")
            return []
        
        query_files = []
        for file in os.listdir(queries_folder):
            if file.endswith(".sql"):
                query_files.append(os.path.join(queries_folder, file))
        
        self.logger.info(f"Found {len(query_files)} query files")
        return query_files
    
    def get_table_name_from_file(self, file_path: str) -> str:
        """Extract table name from SQL file name."""
        file_name = os.path.basename(file_path)
        table_name = os.path.splitext(file_name)[0]
        return table_name
    
    def execute_query_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Execute query file on enabled database(s).
        Returns results from the first available database.
        """
        results = []
        
        # Try SQL Server first if enabled
        if self.sql_service:
            try:
                results = self.sql_service.execute_query_from_file(file_path)
                return results
            except Exception as e:
                self.logger.error(f"SQL Server query failed for {file_path}", e)
        
        # Try Firebird if enabled and SQL Server didn't work
        if self.fb_service:
            try:
                results = self.fb_service.execute_query_from_file(file_path)
                return results
            except Exception as e:
                self.logger.error(f"Firebird query failed for {file_path}", e)
        
        # If we get here, both failed or no database is configured
        if not results:
            raise Exception(f"Failed to execute query from {file_path}")
        
        return results
    
    def sync_single_query(self, query_file: str) -> bool:
        """
        Sync a single query file.
        
        Args:
            query_file: Path to SQL query file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            table_name = self.get_table_name_from_file(query_file)
            self.logger.info(f"Processing query file: {query_file} -> table: {table_name}")
            
            # Execute query
            data = self.execute_query_file(query_file)
            
            if not data:
                self.logger.warning(f"No data returned for {table_name}")
                return True
            
            # Upload to API
            if self.api_service:
                self.api_service.bulk_upsert(table_name, data)
                return True
            else:
                self.logger.error("API service not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to sync {query_file}", e)
            return False
    
    def run_sync(self) -> Dict[str, Any]:
        """
        Run full sync process.
        
        Returns:
            Dictionary with sync results
        """
        start_time = datetime.now()
        self.logger.info("=" * 50)
        self.logger.info(f"Starting sync at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 50)
        
        results = {
            "start_time": start_time,
            "success_count": 0,
            "failed_count": 0,
            "failed_files": []
        }
        
        # Get query files
        query_files = self.get_query_files()
        
        if not query_files:
            self.logger.warning("No query files found")
            return results
        
        # Process each query file
        for query_file in query_files:
            success = self.sync_single_query(query_file)
            
            if success:
                results["success_count"] += 1
            else:
                results["failed_count"] += 1
                results["failed_files"].append(query_file)
        
        # Log summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.logger.info("=" * 50)
        self.logger.info(f"Sync completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Total files: {len(query_files)}")
        self.logger.info(f"Successful: {results['success_count']}")
        self.logger.info(f"Failed: {results['failed_count']}")
        
        if results["failed_files"]:
            self.logger.error(f"Failed files: {', '.join(results['failed_files'])}")
        
        self.logger.info("=" * 50)
        
        results["end_time"] = end_time
        results["duration_seconds"] = duration
        
        return results

def main():
    """Main entry point for sync service."""
    try:
        sync_service = SyncService()
        results = sync_service.run_sync()
        
        # Exit with error code if any syncs failed
        if results["failed_count"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger = Logger("sync")
        logger.error("Fatal error in sync service", e)
        sys.exit(1)

if __name__ == "__main__":
    main()