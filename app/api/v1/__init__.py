"""
Initialize API router with all endpoints.
"""

from fastapi import APIRouter

from . import search  # documents, users, billing require SQLAlchemy - not used

# Create main router
router = APIRouter()

# Include only search router (documents, users, billing disabled - using simple auth)
router.include_router(search.router)

__all__ = ["router"]
