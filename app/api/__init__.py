"""
Initialize API package.
"""

from fastapi import APIRouter
from .v1 import router as v1_router
from .web import router as web_router

router = APIRouter()
# API routes MUST come before web routes so they aren't caught by web_router's catchall
router.include_router(v1_router, prefix="/api/v1")
# Web routes (with catchall 404) come last
router.include_router(web_router)

__all__ = ["router"]
