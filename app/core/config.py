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
    API_DESCRIPTION: str = (
        "A FastAPI-based semantic search platform with vector embeddings and cross-encoder re-ranking"
    )

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Embedding Configuration
    EMBEDDING_MODEL: str = (
        "snowflake/snowflake-arctic-embed-m-v1.5"  # Better semantic understanding than MiniLM
    )
    EMBEDDING_DIMENSION: int = 768  # Arctic uses 768 dimensions (vs MiniLM 384)
    EMBEDDING_USE_ONNX: bool = True  # Use ONNX for better performance
    EMBEDDING_ONNX_DIR: str = (
        "/var/www/readyapi/models/arctic_onnx"  # Production ONNX path
    )
    EMBEDDING_USE_INT8_QUANTIZATION: bool = True  # Enable INT8 quantization by default

    # Search Configuration
    TOP_K: int = 10  # Number of candidates to retrieve before re-ranking
    RERANK_TOP_K: int = 5  # Number of final results to return
    RERANK_MODEL: str = (
        "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"  # Baseline reranker
    )
    ENABLE_RERANKING: bool = (
        False  # Disabled by default (adds 2-5s latency; Arctic-768D is sufficient)
    )

    # Database Configuration
    CHROMA_COLLECTION_NAME: str = "documents"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"

    # CORS Configuration
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]

    # Security Configuration
    API_KEY_HEADER: str = "X-API-Key"
    ADMIN_API_KEY: str = (
        "rapi_admin_change_me_in_env"  # Your personal admin key - CHANGE THIS!
    )
    ENABLE_HTTPS: bool = False  # Set to True in production
    SSL_CERT_FILE: str = "./certs/cert.pem"
    SSL_KEY_FILE: str = "./certs/key.pem"
    REQUIRE_HTTPS: bool = False  # Redirect HTTP to HTTPS

    # Rate Limiting (requests per minute)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 200

    # Email Configuration
    SMTP_HOST: str = "smtp.strato.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "info@readyapi.net"
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "info@readyapi.net"
    BASE_URL: str = "https://readyapi.net"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
