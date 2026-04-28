"""
Initialize API router with all endpoints.
"""

from fastapi import APIRouter

from . import search, documents

# Create main router
router = APIRouter()

# Include all v1 routers
router.include_router(search.router)
router.include_router(documents.router)

__all__ = ["router"]
