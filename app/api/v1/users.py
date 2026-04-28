"""
User management API endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
import logging

from ...core.security import validate_api_key, create_api_key
from ...db.session import get_db_session
from ...models.user import User, APIKey, Usage, Plan
from datetime import datetime, date

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic models for requests/responses
class APIKeyCreate(BaseModel):
    name: str

    class Config:
        json_schema_extra = {"example": {"name": "Production App"}}


class APIKeyResponse(BaseModel):
    id: int
    key_prefix: str
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
    total_requests: int

    class Config:
        from_attributes = True


class APIKeyCreatedResponse(BaseModel):
    key: str
    key_prefix: str
    name: str
    message: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    company: str | None
    plan_name: str
    is_active: bool
    created_at: datetime


class UsageResponse(BaseModel):
    searches_today: int
    searches_this_month: int
    documents_indexed: int
    daily_limit: int
    monthly_limit: int
    remaining_today: int
    remaining_this_month: int


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
) -> UserResponse:
    """
    Get current user information.

    Returns user details associated with the API key.
    """
    if user_context["user_id"] is None:
        # Dev mode
        return UserResponse(
            id=0,
            email="dev@localhost",
            name="Development User",
            company=None,
            plan_name="free",
            is_active=True,
            created_at=datetime.utcnow(),
        )

    user = db.query(User).filter(User.id == user_context["user_id"]).first()

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        company=user.company,
        plan_name=user.plan.name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
) -> UsageResponse:
    """
    Get API usage statistics and limits.
    """
    if user_context["user_id"] is None:
        # Dev mode
        return UsageResponse(
            searches_today=0,
            searches_this_month=0,
            documents_indexed=0,
            daily_limit=100,
            monthly_limit=1000,
            remaining_today=100,
            remaining_this_month=1000,
        )

    user = db.query(User).filter(User.id == user_context["user_id"]).first()
    plan = user.plan

    # Get today's usage
    today = date.today()
    today_usage = (
        db.query(Usage)
        .filter(
            Usage.user_id == user.id,
            Usage.date >= datetime.combine(today, datetime.min.time()),
        )
        .first()
    )

    searches_today = today_usage.searches_count if today_usage else 0

    # Get month's usage
    first_day_of_month = date.today().replace(day=1)
    month_usage = (
        db.query(Usage)
        .filter(
            Usage.user_id == user.id,
            Usage.date >= datetime.combine(first_day_of_month, datetime.min.time()),
        )
        .all()
    )

    searches_this_month = sum(u.searches_count for u in month_usage)
    documents_indexed = sum(u.documents_indexed for u in month_usage)

    return UsageResponse(
        searches_today=searches_today,
        searches_this_month=searches_this_month,
        documents_indexed=documents_indexed,
        daily_limit=plan.searches_per_day,
        monthly_limit=plan.searches_per_month,
        remaining_today=(
            max(0, plan.searches_per_day - searches_today)
            if plan.searches_per_day != -1
            else -1
        ),
        remaining_this_month=(
            max(0, plan.searches_per_month - searches_this_month)
            if plan.searches_per_month != -1
            else -1
        ),
    )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
) -> List[APIKeyResponse]:
    """
    List all API keys for the current user.

    Returns key prefix (first 12 chars) for security, not the full key.
    """
    if user_context["user_id"] is None:
        return []

    api_keys = db.query(APIKey).filter(APIKey.user_id == user_context["user_id"]).all()

    return [APIKeyResponse.model_validate(key) for key in api_keys]


@router.post(
    "/api-keys",
    response_model=APIKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_api_key(
    request: APIKeyCreate,
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
) -> APIKeyCreatedResponse:
    """
    Create a new API key.

    **Important:** The full API key is only shown once. Save it securely!
    """
    if user_context["user_id"] is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create API keys in development mode",
        )

    user = db.query(User).filter(User.id == user_context["user_id"]).first()
    plan = user.plan

    # Check if user has reached max API keys
    current_keys = (
        db.query(APIKey)
        .filter(APIKey.user_id == user.id, APIKey.is_active == True)
        .count()
    )

    if plan.max_api_keys != -1 and current_keys >= plan.max_api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Maximum API keys ({plan.max_api_keys}) reached. Upgrade your plan.",
        )

    # Generate new API key
    new_key = create_api_key()
    key_prefix = new_key[:12] + "..."

    # Save to database
    api_key_record = APIKey(
        key=new_key, key_prefix=key_prefix, name=request.name, user_id=user.id
    )

    db.add(api_key_record)
    db.commit()

    logger.info(f"New API key created for user {user.email}: {key_prefix}")

    return APIKeyCreatedResponse(
        key=new_key,
        key_prefix=key_prefix,
        name=request.name,
        message="API key created successfully. Save it securely - it won't be shown again!",
    )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    user_context: dict = Depends(validate_api_key),
    db: Session = Depends(get_db_session),
):
    """
    Delete (deactivate) an API key.
    """
    if user_context["user_id"] is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete API keys in development mode",
        )

    api_key = (
        db.query(APIKey)
        .filter(APIKey.id == key_id, APIKey.user_id == user_context["user_id"])
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    # Soft delete (deactivate)
    api_key.is_active = False
    db.commit()

    logger.info(
        f"API key deleted: {api_key.key_prefix} for user {user_context['email']}"
    )

    return None
