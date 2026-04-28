"""
API endpoints for semantic search.
"""

from fastapi import APIRouter, HTTPException, status, Header
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
    Perform semantic search with cross-encoder re-ranking.

    Pipeline:
    1. Converts query to embedding
    2. Retrieves similar documents using vector search
    3. Re-ranks results using cross-encoder for better relevance
    4. Returns sorted documents with relevance scores

    **Request Body:**
    - `query`: Search query string (required)
    - `top_k`: Number of results to return (1-50, default: 5)
    - `filters`: Optional metadata filters (filter by category, language, author, etc.)
    - `include_content`: Include document content in results (default: true)

    **Example without filters:**
    ```json
    {
        "query": "How does machine learning work?",
        "top_k": 5,
        "include_content": true
    }
    ```

    **Example with filters:**
    ```json
    {
        "query": "artificial intelligence",
        "top_k": 10,
        "filters": {
            "category": "tutorial",
            "language": "es",
            "author": "John Doe"
        },
        "include_content": true
    }
    ```

    **Available filter fields:**
    Any field in metadata with simple types (str, int, float, bool).

    Auto-indexed field: language
    **Response:**
    - `query`: The original search query
    - `total_results`: Number of results found
    - `results`: Array of ranked documents with:
      - `id`: Document identifier
      - `title`: Document title
      - `score`: Relevance score (0-1)
      - `content`: Document content (if requested)
      - `metadata`: Document metadata
    - `execution_time_ms`: Query execution time
    """
    # Validate API key
    user_context = await _validate_api_key_internal(x_api_key)
    try:
        logger.info(f"Received search query: '{search_query.query}'")

        tenant_id = user_context["tenant_id"]
        search_engine = _get_search_engine_for_tenant(tenant_id)

        # Perform search
        results, execution_time = search_engine.search(
            query=search_query.query,
            top_k=search_query.top_k,
            filters=search_query.filters,
            include_content=search_query.include_content,
        )

        # Format results
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

        # Track usage if user is authenticated
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

        response = SearchResponse(
            query=search_query.query,
            total_results=len(formatted_results),
            results=formatted_results,
            execution_time_ms=execution_time,
        )

        logger.info(
            f"Search completed. Found {len(formatted_results)} results in {execution_time:.2f}ms"
        )
        return response

    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing search: {str(e)}",
        )


@router.get("/health", tags=["Search"], include_in_schema=False)
async def health_check() -> dict:
    """
    Health check endpoint for the search service.

    **Returns:**
    - `status`: Service status
    - `message`: Status message
    """
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
    """
    Get total searches for current month.

    Requires valid API key in header.

    **Returns:**
    - `month`: Current month (YYYY-MM)
    - `total_searches`: Total searches this month

    **Example:**
    ```bash
    curl -H "X-API-Key: YOUR_API_KEY" https://readyapi.net/api/v1/search/stats/monthly
    ```
    """
    from datetime import datetime, date

    try:
        # Validate API key using internal function
        user_context = await _validate_api_key_internal(x_api_key)

        if not user_context.get("user_id"):
            # Dev mode - return dummy stats
            current_month = datetime.utcnow().strftime("%Y-%m")
            return {
                "month": current_month,
                "total_searches": 0,
                "note": "Development mode - no tracking",
            }

        # Get monthly stats from database
        from app.db.session import SessionLocal
        from app.models.user import Usage

        db = SessionLocal()
        try:
            # Get first day of current month
            today = date.today()
            first_day = today.replace(day=1)

            # Query usage records for this month
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
