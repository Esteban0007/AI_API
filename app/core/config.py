"""
Configuration module for the semantic search SaaS application.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # API Configuration
    API_TITLE: str = "Semantic Search SaaS API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "A FastAPI-based semantic search platform with vector embeddings and cross-encoder re-ranking"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"  # Fast and lightweight
    EMBEDDING_DIMENSION: int = 384
    
    # Search Configuration
    TOP_K: int = 10  # Number of candidates to retrieve before re-ranking
    RERANK_TOP_K: int = 5  # Number of final results to return
    RERANK_MODEL: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"  # Lightweight cross-encoder
    
    # Database Configuration
    CHROMA_COLLECTION_NAME: str = "documents"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # API Keys (for future SaaS features)
    API_KEY_HEADER: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
