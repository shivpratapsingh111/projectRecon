# url_monitor/config.py
import yaml
from pathlib import Path

def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file"""
    default_config = {
        'database': {
            'dbname': 'projectrecon',
            'user': 'postgres',
            'password': 'postgres',
            'host': 'localhost',
            'port': 5432
        }
    }
    
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file) as f:
            config = yaml.safe_load(f)
            return {**default_config, **config}
    return default_config

