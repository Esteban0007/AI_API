"""
Initialize API router with all endpoints.
"""

from fastapi import APIRouter

# Ponemos 'shopify' al final de la lista de imports
from . import search, documents, shopify

# Create main router
router = APIRouter()

# Include all v1 routers
router.include_router(search.router)
router.include_router(documents.router)
router.include_router(shopify.router, prefix="/shopify", tags=["Shopify"])

__all__ = ["router"]
