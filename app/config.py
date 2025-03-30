"""
Configuration management for DocuChat
"""
import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

def load_config():
    """
    Load configuration from config.yaml and environment variables
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the base directory (project root)
    base_dir = Path(__file__).resolve().parent.parent
    
    # Load config from YAML file
    config_path = base_dir / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Add MongoDB connection string from environment variables
    config["mongo_connection_string"] = os.getenv("MONGO_CONNECTION_STR")
    
    # Add any additional environment variables
    config["ollama_host"] = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    config["ollama_embed_host"] = os.getenv("OLLAMA_EMBED_HOST", "http://localhost:11434")
    
    return config