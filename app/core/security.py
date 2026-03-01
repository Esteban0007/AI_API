"""
Security module for API authentication and validation.
"""

from fastapi import HTTPException, status, Header
from typing import Optional
from datetime import datetime, date
import logging
import sqlite3

from .config import get_settings

logger = logging.getLogger(__name__)
DB_PATH = "./data/users.db"


async def validate_api_key(
    x_api_key: Optional[str] = Header(None),
) -> dict:
    """
    Validate API key from request header using SQLite.

    Returns:
        dict with user_id, email, plan, and limits

    Raises:
        HTTPException: If API key is invalid or user exceeded limits
    """
    settings = get_settings()

    # Check if it's the ADMIN API KEY (highest priority)
    if x_api_key and x_api_key == settings.ADMIN_API_KEY:
        logger.info("Admin API key used - unlimited access granted")
        # Admin has its own isolated tenant
        return {
            "user_id": None,
            "email": "admin@readyapi.net",
            "name": "Administrator",
            "plan": "admin",
            "is_admin": True,
            "api_key": x_api_key,
            "tenant_id": "admin",
        }

    # In development, allow requests without API key
    if settings.DEBUG and not x_api_key:
        logger.warning("Development mode: Request without API key")
        return {
            "user_id": None,
            "email": "dev@localhost",
            "plan": "free",
            "is_admin": False,
            "api_key": "dev-key",
            "tenant_id": "dev",
        }

    # Production: require API key
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include 'X-API-Key' header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate API key format
    if not x_api_key.startswith("rapi_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )

    # Query SQLite database for API key
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT id, email, is_confirmed FROM users WHERE api_key = ?", (x_api_key,)
        )
        user_record = c.fetchone()
        conn.close()
    except Exception as e:
        logger.error(f"Database error validating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error",
        )

    if not user_record:
        logger.warning(f"Invalid API key attempt: {x_api_key[:12]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    user_id, email, is_confirmed = user_record

    # Check if user has confirmed email
    if not is_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed. Please confirm your email first.",
        )

    # Return user context
    return {
        "user_id": user_id,
        "email": email,
        "name": email.split("@")[0],
        "plan": "pro",
        "is_admin": False,
        "api_key": x_api_key,
        "tenant_id": f"user_{user_id}",
    }


def create_api_key(length: int = 32) -> str:
    """
    Generate a secure random API key.

    Format: rapi_<random_string>
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    random_part = "".join(secrets.choice(alphabet) for _ in range(length))

    return f"rapi_{random_part}"
