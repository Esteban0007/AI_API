"""
Initialize API router with all endpoints.
"""

from fastapi import APIRouter

from . import search, documents, shopify

# Create main router
router = APIRouter()

# Include all v1 routers
router.include_router(search.router)
router.include_router(documents.router)

router.include_router(shopify.router, prefix="/shopify", tags=["Shopify Integration"])

__all__ = ["router"]
