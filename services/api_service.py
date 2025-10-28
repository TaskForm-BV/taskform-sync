import requests
import time
from typing import List, Dict, Any
from utils.logging import Logger

class APIService:
    """Service for API operations with retry logic."""
    
    def __init__(self, base_url: str, api_key: str, tenant_id: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.logger = Logger("api")
        
        # Retry settings
        self.max_retries = 3
        self.initial_retry_delay = 1  # seconds
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
            "X-Tenant-ID": self.tenant_id
        }
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            # Try a simple GET request to the base URL
            response = requests.get(
                self.base_url,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code < 500:
                self.logger.success("API connection successful")
                return True
            else:
                raise Exception(f"API returned status code: {response.status_code}")
                
        except Exception as e:
            self.logger.error("API connection failed", e)
            raise Exception(f"API connection failed: {str(e)}")
    
    def bulk_upsert(self, table_name: str, data: List[Dict[str, Any]], key_field: str = "external_id") -> bool:
        """
        Perform bulk upsert operation.
        
        Args:
            table_name: Name of the table to upsert into
            data: List of data dictionaries to upsert
            key_field: Field name to use as the key for upsert operation
        
        Returns:
            True if successful, raises exception otherwise
        """
        if not data:
            self.logger.warning(f"No data to upsert for table: {table_name}")
            return True
        
        endpoint = f"{self.base_url}/{table_name}/bulk"
        payload = {
            "data": data,
            "operation": "upsert",
            "keyField": key_field
        }
        
        self.logger.info(f"Bulk upserting {len(data)} records to {table_name}")
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    self.logger.success(f"Bulk upsert successful for {table_name}: {len(data)} records")
                    return True
                elif response.status_code >= 500:
                    # Server error, retry
                    raise Exception(f"Server error: {response.status_code} - {response.text}")
                else:
                    # Client error, don't retry
                    self.logger.error(f"Bulk upsert failed for {table_name}: {response.status_code} - {response.text}")
                    raise Exception(f"API error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    delay = self.initial_retry_delay * (2 ** attempt)
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"All retry attempts failed for {table_name}", e)
                    raise Exception(f"Bulk upsert failed after {self.max_retries} attempts: {str(e)}")
        
        return False