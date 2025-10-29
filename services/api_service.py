import requests
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Union
from utils.logging import Logger

class APIService:
    """Service for API operations with retry logic."""
    
    def __init__(self, base_url: str, api_key: str, tenant_id: str, dry_run: bool = False):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.dry_run = dry_run
        self.logger = Logger("api")
        
        # Retry settings
        self.max_retries = 3
        self.initial_retry_delay = 1  # seconds
        
        if self.dry_run:
            self.logger.info("🧪 DRY-RUN MODE ENABLED - No data will be sent to API")
            # Create dry-run output folder
            self.dry_run_folder = "dry-run-output"
            os.makedirs(self.dry_run_folder, exist_ok=True)

    def _lowercase_json(self, value: Union[Dict[str, Any], List[Any], str, Any]) -> Union[Dict[str, Any], List[Any], str, Any]:
        """Recursively convert all dictionary keys and string values to lowercase."""
        if isinstance(value, dict):
            return {str(key).lower(): self._lowercase_json(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._lowercase_json(item) for item in value]
        if isinstance(value, str):
            return value.lower()
        return value
    
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
        transformed_data = self._lowercase_json(data)
        transformed_key_field = key_field.lower() if isinstance(key_field, str) else key_field

        payload = {
            "data": transformed_data,
            "operation": "upsert",
            "keyField": transformed_key_field
        }
        
        self.logger.info(f"📊 Processing {len(data)} records for table: {table_name}")
        self.logger.info(f"🌐 Target URL: {endpoint}")
        
        # DRY-RUN MODE: Save to JSON file instead of posting
        if self.dry_run:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.dry_run_folder, f"{table_name}_{timestamp}.json")
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
                
                self.logger.success(f"🧪 DRY-RUN: Saved {len(data)} records to {output_file}")
                self.logger.info(f"   Would POST to: {endpoint}")
                self.logger.info(f"   Payload size: {len(json.dumps(payload))} bytes")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to save dry-run output", e)
                return False
        
        # NORMAL MODE: Actually post to API
        self.logger.info(f"📤 Bulk upserting {len(data)} records to {table_name}")
        
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