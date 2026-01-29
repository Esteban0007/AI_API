"""
Security module for API authentication and validation.
"""

from fastapi import HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date
import logging

from .config import get_settings
from ..db.session import get_db_session
from ..models.user import APIKey, User, Usage

logger = logging.getLogger(__name__)


async def validate_api_key(
    x_api_key: Optional[str] = Header(None), db: Session = Depends(get_db_session)
) -> dict:
    """
    Validate API key from request header and return user context.

    Returns:
        dict with user_id, email, plan, and limits

    Raises:
        HTTPException: If API key is invalid or user exceeded limits
    """
    settings = get_settings()

    # Check if it's the ADMIN API KEY (highest priority)
    if x_api_key and x_api_key == settings.ADMIN_API_KEY:
        logger.info("Admin API key used - unlimited access granted")
        return {
            "user_id": None,
            "email": "admin@readyapi.net",
            "name": "Administrator",
            "plan": "admin",
            "is_admin": True,
            "api_key": x_api_key
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

    # Query database for API key
    api_key_record = (
        db.query(APIKey)
        .filter(APIKey.key == x_api_key, APIKey.is_active == True)
        .first()
    )

    if not api_key_record:
        logger.warning(f"Invalid API key attempt: {x_api_key[:12]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    # Check if API key expired
    if api_key_record.expires_at and api_key_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
        )

    # Get user
    user = db.query(User).filter(User.id == api_key_record.user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Check subscription status
    if user.subscription_status not in ["active", "trialing"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Subscription {user.subscription_status}. Please update payment.",
        )

    # Update last used timestamp
    api_key_record.last_used_at = datetime.utcnow()
    api_key_record.total_requests += 1
    db.commit()

    # Return user context
    return {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "plan": user.plan.name,
        "api_key": x_api_key,
    }


async def check_rate_limit(
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
) -> dict:
    """
    Check if user has exceeded rate limits.

    Returns:
        User context with usage info

    Raises:
        HTTPException: If rate limit exceeded
    """
    # Skip for dev mode
    if user_context["user_id"] is None:
        return user_context

    user_id = user_context["user_id"]
    # Admin users bypass all rate limiting
    if user_context.get("is_admin"):
        user_context["rate_limited"] = False
        return user_context

    # Get user and plan
    user = db.query(User).filter(User.id == user_id).first()
    plan = user.plan

    # Get or create today's usage record
    today = date.today()
    usage = (
        db.query(Usage)
        .filter(
            Usage.user_id == user_id,
            Usage.date >= datetime.combine(today, datetime.min.time()),
        )
        .first()
    )

    if not usage:
        usage = Usage(user_id=user_id, date=datetime.utcnow())
        db.add(usage)
        db.commit()

    # Check daily limit
    if plan.searches_per_day != -1 and usage.searches_count >= plan.searches_per_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily limit of {plan.searches_per_day} searches exceeded. Upgrade your plan.",
        )

    # Increment usage counter
    usage.searches_count += 1
    usage.updated_at = datetime.utcnow()
    db.commit()

    # Add usage info to context
    user_context["usage"] = {
        "searches_today": usage.searches_count,
        "daily_limit": plan.searches_per_day,
        "remaining_today": (
            plan.searches_per_day - usage.searches_count
            if plan.searches_per_day != -1
            else -1
        ),
    }
    user_context["is_admin"] = False
    user_context["rate_limited"] = True

    return user_context


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
