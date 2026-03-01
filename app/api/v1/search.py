"""
API endpoints for semantic search.
"""

from fastapi import APIRouter, HTTPException, status, Header
import logging
from typing import Optional

from ...models.search import SearchQuery, SearchResponse, SearchResult
from ...core.security import validate_api_key
from ...engine.searcher import SearchEngine
from ...engine.store import VectorStore
from ...engine.embedder import Embedder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["Search"])

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
    user_context = await validate_api_key(x_api_key)
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
