"""
Configuration management for the Vulnerability Scanner.
Supports loading settings from JSON config files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "scanner": {
        "timeout": 1.5,
        "max_workers": 100,
        "port_range": [1, 65535],
        "max_ports": 65535,
        "retry_count": 1,
    },
    "banner_grabbing": {
        "timeout": 3,
        "max_banner_size": 4096,
    },
    "reporting": {
        "formats": ["pdf"],
        "output_dir": "reports",
    },
    "logging": {
        "level": "INFO",
        "file": "scanner.log",
    }
}


class Config:
    """Configuration manager for the vulnerability scanner."""

    def __init__(self, config_file: str = None):
        """Initialize configuration from file or use defaults."""
        self.config = DEFAULT_CONFIG.copy()

        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        else:
            # Look for config in standard locations
            for location in self._get_config_locations():
                if os.path.exists(location):
                    self.load_from_file(location)
                    break

    def load_from_file(self, filepath: str):
        """Load configuration from JSON file."""
        try:
            with open(filepath, 'r') as f:
                user_config = json.load(f)
                self._merge_config(self.config, user_config)
            print(f"[Config] Loaded configuration from {filepath}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Config] Error loading config file: {e}. Using defaults.")

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Recursively merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _get_config_locations(self):
        """Return list of possible config file locations."""
        locations = [
            "config.json",
            os.path.expanduser("~/.vulnscanner/config.json"),
            "/etc/vulnscanner/config.json",
        ]
        # Add current script directory
        script_dir = Path(__file__).parent
        locations.insert(0, str(script_dir / "config.json"))
        return locations

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'scanner.timeout')."""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def save_to_file(self, filepath: str):
        """Save current configuration to JSON file."""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"[Config] Configuration saved to {filepath}")
        except IOError as e:
            print(f"[Config] Error saving config file: {e}")

    def create_default_config(self, filepath: str = "config.json"):
        """Create a default configuration file."""
        self.save_to_file(filepath)


# Global config instance
_config = None


def get_config(config_file: str = None) -> Config:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config
