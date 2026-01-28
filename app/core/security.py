"""
Security module for API authentication and validation.
"""
from fastapi import HTTPException, status, Header
from typing import Optional
from .config import get_settings


async def validate_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Validate API key from request header.
    
    For now, this is a placeholder. In a production SaaS,
    you would validate against a database of valid API keys.
    """
    settings = get_settings()
    
    # In development, allow requests without API key
    if settings.DEBUG:
        return x_api_key or "dev-key"
    
    # In production, require valid API key
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Validate against database of valid API keys
    return x_api_key
