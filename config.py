import json
import os
import shutil
from typing import Dict, Any, Optional
from utils.encryption import encrypt_string, decrypt_string, is_encrypted

class Config:
    """Configuration manager for DataSync application with encrypted credentials."""
    
    # Fields that should be encrypted
    ENCRYPTED_FIELDS = [
        "api.api_key",
        "firebird.password"
    ]
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.template_path = "config.template.json"
        self.config: Dict[str, Any] = self._load_default_config()
        self._ensure_config_exists()
        self.load()
    
    def _ensure_config_exists(self) -> None:
        """Ensure config.json exists, copy from template if needed."""
        if not os.path.exists(self.config_path):
            if os.path.exists(self.template_path):
                # Copy template to config.json
                try:
                    shutil.copy(self.template_path, self.config_path)
                    print(f"Created {self.config_path} from template")
                except Exception as e:
                    print(f"Warning: Could not copy template: {e}")
            else:
                # Create config with defaults if no template exists
                self.save()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "sql_server": {
                "enabled": False,
                "connection_string": ""
            },
            "firebird": {
                "enabled": False,
                "database_path": "",
                "username": "",
                "password": ""
            },
            "api": {
                "base_url": "",
                "api_key": "",
                "tenant_id": ""
            },
            "sync": {
                "queries_folder": "queries",
                "log_level": "INFO",
                "batch_size": 1000,
                "dry_run": False
            }
        }
    
    def load(self) -> None:
        """Load configuration from file and decrypt sensitive fields."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    
                # Decrypt sensitive fields
                for field in self.ENCRYPTED_FIELDS:
                    encrypted_value = self.get(field, "")
                    if encrypted_value and is_encrypted(encrypted_value):
                        try:
                            decrypted_value = decrypt_string(encrypted_value)
                            self.set(field, decrypted_value)
                        except Exception as e:
                            print(f"Warning: Could not decrypt {field}: {e}")
                            
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save(self) -> None:
        """Save configuration to file with encrypted sensitive fields."""
        try:
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else ".", exist_ok=True)
            
            # Create a copy of config for saving
            config_to_save = json.loads(json.dumps(self.config))  # Deep copy
            
            # Encrypt sensitive fields before saving
            for field in self.ENCRYPTED_FIELDS:
                plaintext_value = self.get(field, "")
                if plaintext_value and not is_encrypted(plaintext_value):
                    encrypted_value = encrypt_string(plaintext_value)
                    # Set encrypted value in the copy
                    keys = field.split('.')
                    target = config_to_save
                    for k in keys[:-1]:
                        target = target[k]
                    target[keys[-1]] = encrypted_value
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            raise Exception(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def get_sql_server_config(self) -> Dict[str, Any]:
        """Get SQL Server configuration."""
        return self.config.get("sql_server", {})
    
    def get_firebird_config(self) -> Dict[str, Any]:
        """Get Firebird configuration."""
        return self.config.get("firebird", {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self.config.get("api", {})
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get sync configuration."""
        return self.config.get("sync", {})
    
    def is_sql_server_enabled(self) -> bool:
        """Check if SQL Server is enabled."""
        return self.get("sql_server.enabled", False)
    
    def is_firebird_enabled(self) -> bool:
        """Check if Firebird is enabled."""
        return self.get("firebird.enabled", False)