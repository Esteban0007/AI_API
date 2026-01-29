"""
API endpoints for semantic search.
"""

from fastapi import APIRouter, HTTPException, status, Depends
import logging

from ...models.search import SearchQuery, SearchResponse, SearchResult
from ...core.security import validate_api_key, check_rate_limit
from ...engine.searcher import SearchEngine
from ...engine.store import VectorStore
from ...engine.embedder import Embedder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/search", tags=["search"])

# Global instances
embedder = Embedder()
vector_store = VectorStore(embedder=embedder)
search_engine = SearchEngine(vector_store=vector_store, embedder=embedder)


@router.post("/query", response_model=SearchResponse)
async def search(
    search_query: SearchQuery,
    user_context: dict = Depends(check_rate_limit),  # ← Validates API key + rate limits
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
    - `filters`: Optional metadata filters
    - `include_content`: Include document content in results (default: true)

    **Example:**
    ```json
    {
        "query": "How does machine learning work?",
        "top_k": 5,
        "include_content": true
    }
    ```

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
    try:
        logger.info(f"Received search query: '{search_query.query}'")

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
                metadata=result.get("metadata"),
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


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for the search service.

    **Returns:**
    - `status`: Service status
    - `message`: Status message
    - `collection_stats`: Statistics about the document collection
    """
    try:
        stats = search_engine.get_collection_stats()
        return {
            "status": "healthy",
            "message": "Search service is running",
            "collection_stats": stats,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service is unavailable",
        )
