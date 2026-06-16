from fastapi import APIRouter

from . import search, documents, shopify

router = APIRouter()

router.include_router(search.router)
router.include_router(documents.router)
router.include_router(shopify.router, prefix="/shopify", tags=["Shopify Integration"])

__all__ = ["router"]
