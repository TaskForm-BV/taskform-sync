import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from config import Config
from services.sqlserver_service import SQLServerService
from services.firebird_service import FirebirdService
from services.api_service import APIService
from utils.logging import Logger
from utils.transformers import auto_nest_data

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
        sync_config = self.config.get_sync_config()
        dry_run = sync_config.get("dry_run", False)
        
        if all([api_config.get("base_url"), api_config.get("api_key"), api_config.get("tenant_id")]):
            self.api_service = APIService(
                api_config["base_url"],
                api_config["api_key"],
                api_config["tenant_id"],
                dry_run=dry_run
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
        
        file_map = {}
        for file in os.listdir(queries_folder):
            if file.endswith(".sql"):
                file_map[file] = os.path.join(queries_folder, file)

        if not file_map:
            self.logger.info("Found 0 query files")
            return []

        ordered_files: List[str] = []
        configured_order = sync_config.get("query_order", []) if isinstance(sync_config, dict) else []
        seen = set()

        if configured_order:
            for entry in configured_order:
                if not isinstance(entry, str):
                    self.logger.warning(f"Configured query name is not a string: {entry}")
                    continue
                file_name = entry if entry.endswith(".sql") else f"{entry}.sql"
                if file_name in file_map:
                    ordered_files.append(file_map[file_name])
                    seen.add(file_name)
                else:
                    self.logger.warning(f"Configured query not found: {file_name}")

        for file_name in sorted(file_map.keys()):
            if file_name not in seen:
                ordered_files.append(file_map[file_name])

        self.logger.info(f"Found {len(ordered_files)} query files")

        if configured_order:
            self.logger.info("Using configured query order where applicable")
        else:
            self.logger.info("Using default alphabetical query order")

        return ordered_files
    
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
            
            # Auto-nest data if query uses dot notation (e.g., lines.sku, lines.steps.name)
            # Queries with 'parent-id' column will be automatically nested
            nested_data = auto_nest_data(data)
            
            # Log transformation if nesting occurred
            if len(nested_data) != len(data):
                self.logger.info(f"Nested {len(data)} rows into {len(nested_data)} parent records")
            
            # Upload to API
            if self.api_service:
                self.api_service.bulk_upsert(table_name, nested_data)
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