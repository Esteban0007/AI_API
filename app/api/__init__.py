"""
Initialize API package.
"""

from fastapi import APIRouter
from .v1 import router as v1_router
from .web import router as web_router

router = APIRouter()
router.include_router(web_router)
router.include_router(v1_router, prefix="/api/v1")

__all__ = ["router"]
