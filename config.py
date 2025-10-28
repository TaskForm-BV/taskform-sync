import json
import os
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for DataSync application."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = self._load_default_config()
        self.load()
    
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
                "interval_minutes": 30,
                "queries_folder": "queries"
            }
        }
    
    def load(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else ".", exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
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