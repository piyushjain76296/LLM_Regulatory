"""Configuration management for the regulatory reporting assistant."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Vector Database
    chroma_db_path: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Application Settings
    debug: bool = True
    demo_mode: bool = True  # Set to True to use demo responses without OpenAI API
    max_retrieval_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
