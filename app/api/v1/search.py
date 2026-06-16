"""
API endpoints for semantic search.
"""

from fastapi import APIRouter, HTTPException, status, Header, Query
import logging
from typing import Optional

from ...models.search import SearchQuery, SearchResponse, SearchResult
from ...core.security import validate_api_key, _validate_api_key_internal
from ...engine.searcher import SearchEngine
from ...engine.store import VectorStore
from ...engine.embedder import Embedder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

# Global instances
embedder = Embedder()
_vector_store_cache: dict[str, VectorStore] = {}
_search_engine_cache: dict[str, SearchEngine] = {}


def _get_vector_store_for_tenant(tenant_id: str) -> VectorStore:
    if tenant_id not in _vector_store_cache:
        _vector_store_cache[tenant_id] = VectorStore(
            embedder=embedder, tenant_id=tenant_id
        )
    return _vector_store_cache[tenant_id]


def _get_search_engine_for_tenant(tenant_id: str) -> SearchEngine:
    if tenant_id not in _search_engine_cache:
        vector_store = _get_vector_store_for_tenant(tenant_id)
        _search_engine_cache[tenant_id] = SearchEngine(
            vector_store=vector_store, embedder=embedder
        )
    return _search_engine_cache[tenant_id]


@router.post("/query", response_model=SearchResponse)
async def search(
    search_query: SearchQuery,
    x_api_key: Optional[str] = Header(None),
) -> SearchResponse:
    """
    Perform semantic search with cross-encoder re-ranking using API Key.
    """
    user_context = await _validate_api_key_internal(x_api_key)
    try:
        logger.info(f"Received search query: '{search_query.query}'")

        tenant_id = user_context["tenant_id"]
        search_engine = _get_search_engine_for_tenant(tenant_id)

        results, execution_time = search_engine.search(
            query=search_query.query,
            top_k=search_query.top_k,
            filters=search_query.filters,
            include_content=search_query.include_content,
        )

        formatted_results = [
            SearchResult(
                id=result["id"],
                title=result["title"],
                score=result["score"],
                content=result.get("content"),
                metadata={
                    k: v
                    for k, v in result.get("metadata", {}).items()
                    if k != "tenant_id"
                },
            )
            for result in results
        ]

        if user_context.get("user_id"):
            try:
                from ...db.session import SessionLocal
                from ...models.user import Usage
                from datetime import date, datetime

                db = SessionLocal()
                today = date.today()
                usage = (
                    db.query(Usage)
                    .filter(
                        Usage.user_id == user_context["user_id"],
                        Usage.date >= datetime.combine(today, datetime.min.time()),
                    )
                    .first()
                )

                if not usage:
                    usage = Usage(
                        user_id=user_context["user_id"],
                        date=datetime.utcnow(),
                        searches_count=0,
                    )
                    db.add(usage)

                usage.searches_count = (usage.searches_count or 0) + 1
                db.commit()
                db.close()
            except Exception as e:
                logger.warning(f"Failed to track usage: {e}")

        return SearchResponse(
            query=search_query.query,
            total_results=len(formatted_results),
            results=formatted_results,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}",
        )


@router.post("/shopify-query", response_model=SearchResponse)
async def shopify_search_dynamic(
    search_query: SearchQuery,
    x_shopify_shop_domain: Optional[str] = Header(None, alias="X-Shopify-Shop-Domain"),
) -> SearchResponse:
    """
    Endpoint POST dinámico para Shopify que soporta filtros complejos en el JSON.
    Identifica al tenant en la base de datos usando la cabecera X-Shopify-Shop-Domain.
    """
    if not x_shopify_shop_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Falta la cabecera X-Shopify-Shop-Domain para identificar la tienda",
        )

    from app.db.users import get_user_by_shopify_domain

    user_context = get_user_by_shopify_domain(x_shopify_shop_domain)

    if not user_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La tienda {x_shopify_shop_domain} no está registrada",
        )

    try:
        logger.info(
            f"Búsqueda con filtros desde Shopify [{x_shopify_shop_domain}]: '{search_query.query}'"
        )

        tenant_id = (
            user_context["tenant_id"]
            if "tenant_id" in user_context
            else f"user_{user_context['id']}"
        )
        search_engine = _get_search_engine_for_tenant(tenant_id)

        results, execution_time = search_engine.search(
            query=search_query.query,
            top_k=search_query.top_k,
            filters=search_query.filters,  # Filtros dinámicos aplicados aquí
            include_content=search_query.include_content,
        )

        formatted_results = [
            SearchResult(
                id=result["id"],
                title=result["title"],
                score=result["score"],
                content=result.get("content"),
                metadata={
                    k: v
                    for k, v in result.get("metadata", {}).items()
                    if k != "tenant_id"
                },
            )
            for result in results
        ]

        return SearchResponse(
            query=search_query.query,
            total_results=len(formatted_results),
            results=formatted_results,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.error(f"Error en búsqueda con filtros desde Shopify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/health", tags=["Search"], include_in_schema=False)
async def health_check() -> dict:
    try:
        return {
            "status": "healthy",
            "message": "Search service is running",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service is unavailable",
        )


@router.get("/stats/monthly")
async def get_monthly_stats(
    x_api_key: Optional[str] = Header(None),
) -> dict:
    from datetime import datetime, date

    try:
        user_context = await _validate_api_key_internal(x_api_key)
        if not user_context.get("user_id"):
            current_month = datetime.utcnow().strftime("%Y-%m")
            return {
                "month": current_month,
                "total_searches": 0,
                "note": "Development mode - no tracking",
            }

        from app.db.session import SessionLocal
        from app.models.user import Usage

        db = SessionLocal()
        try:
            today = date.today()
            first_day = today.replace(day=1)
            monthly_usage = (
                db.query(Usage)
                .filter(
                    Usage.user_id == user_context["user_id"],
                    Usage.date >= datetime.combine(first_day, datetime.min.time()),
                )
                .all()
            )
            total_searches = sum(u.searches_count for u in monthly_usage)
            current_month = today.strftime("%Y-%m")
            return {"month": current_month, "total_searches": total_searches}
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error getting monthly stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving monthly statistics",
        )
