"""
Initialize API router with all endpoints.
"""

from fastapi import APIRouter

from . import search, documents, users, billing

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(documents.router)
router.include_router(search.router)
router.include_router(users.router)
router.include_router(billing.router)

__all__ = ["router"]
