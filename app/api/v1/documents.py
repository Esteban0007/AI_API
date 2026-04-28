"""
API endpoints for document management.
"""

from fastapi import APIRouter, HTTPException, status, Header
import logging
from typing import List, Optional

from ...models.document import DocumentCreate, DocumentBatch, DocumentResponse
from ...models.search import DocumentUploadResponse
from ...core.security import validate_api_key, _validate_api_key_internal
from ...engine.store import VectorStore
from ...engine.embedder import Embedder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Maximum docs to embed in a single internal chunk (avoids OOM)
INTERNAL_CHUNK_SIZE = 50

# Global instances
embedder = Embedder()
_vector_store_cache: dict[str, VectorStore] = {}


def _get_vector_store_for_tenant(tenant_id: str) -> VectorStore:
    if tenant_id not in _vector_store_cache:
        _vector_store_cache[tenant_id] = VectorStore(
            embedder=embedder, tenant_id=tenant_id
        )
    return _vector_store_cache[tenant_id]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    batch: DocumentBatch,
    x_api_key: Optional[str] = Header(None),
) -> DocumentUploadResponse:
    """
    Upload and index documents.

    Generates embeddings and stores documents in the vector database.

    **Request Body:**
    - `documents`: List of documents with id, title, content, optional keywords and metadata

    **Example:**
    ```json
    {
        "documents": [
            {
                "id": "doc-001",
                "title": "Machine Learning Basics",
                "content": "Machine learning is a subset of artificial intelligence...",
                "keywords": ["ml", "ai"],
                "metadata": {
                    "category": "tutorial",
                    "language": "es",
                    "source": "https://example.com"
                }
            }
        ]
    }
    ```

    **Response:**
    - `success`: Whether the operation was successful
    - `uploaded_count`: Number of documents successfully uploaded
    - `failed_count`: Number of documents that failed
    """
    # Validate API key
    user_context = await _validate_api_key_internal(x_api_key)
    try:
        if not batch.documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Empty document batch"
            )

        logger.info(f"Uploading batch of {len(batch.documents)} documents")

        # Prepare documents for batch upload
        docs_to_upload = []
        for doc in batch.documents:
            docs_to_upload.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "keywords": doc.keywords or [],
                    "metadata": doc.metadata or {},
                }
            )

        tenant_id = user_context["tenant_id"]
        vector_store = _get_vector_store_for_tenant(tenant_id)

        # Process internally in chunks of INTERNAL_CHUNK_SIZE
        # so the client never has to worry about batch size limits
        total_ok = 0
        total_fail = 0
        for i in range(0, len(docs_to_upload), INTERNAL_CHUNK_SIZE):
            chunk = docs_to_upload[i : i + INTERNAL_CHUNK_SIZE]
            ok, fail = vector_store.add_documents_batch(chunk)
            total_ok += ok
            total_fail += fail
            logger.info(
                f"Chunk {i // INTERNAL_CHUNK_SIZE + 1}: "
                f"{ok} ok, {fail} fail "
                f"(total {total_ok}/{len(docs_to_upload)})"
            )

        return DocumentUploadResponse(
            success=total_fail == 0,
            message=(
                f"Successfully uploaded {total_ok} documents"
                if total_fail == 0
                else f"Partial upload: {total_ok} succeeded, {total_fail} failed"
            ),
            uploaded_count=total_ok,
            failed_count=total_fail,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading documents: {str(e)}",
        )


@router.get("/stats")
async def get_stats(x_api_key: Optional[str] = Header(None)) -> dict:
    """
    Get statistics about the document collection.

    **Returns:**
    - `document_count`: Total number of indexed documents
    - `embedding_dimension`: Dimension of embeddings
    - `model`: Model used for embeddings
    """
    # Validate API key
    user_context = await _validate_api_key_internal(x_api_key)

    try:
        tenant_id = user_context["tenant_id"]
        vector_store = _get_vector_store_for_tenant(tenant_id)
        stats = vector_store.get_collection_stats()
        # Remove collection_name from response
        stats.pop("collection_name", None)
        stats.pop("tenant_id", None)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics",
        )


@router.get("/all")
async def get_all_documents(x_api_key: Optional[str] = Header(None)) -> dict:
    """
    Get all documents in the collection as JSON.

    Returns all indexed documents with their metadata.

    **Returns:**
    - `documents`: Array of all documents with id, content, and metadata
    - `total_documents`: Total count of documents
    - `collection_name`: Name of the collection

    **Example:**
    ```bash
    curl -H "X-API-Key: YOUR_API_KEY" https://readyapi.net/api/v1/documents/all
    ```
    """
    # Validate API key
    user_context = await _validate_api_key_internal(x_api_key)

    try:
        tenant_id = user_context["tenant_id"]
        vector_store = _get_vector_store_for_tenant(tenant_id)

        # Get all documents
        all_docs = vector_store.get_all_documents()

        return {
            "documents": all_docs,
            "total_documents": len(all_docs),
            "collection_name": vector_store.collection_name,
        }
    except Exception as e:
        logger.error(f"Error getting all documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving documents",
        )


@router.delete("/clear-all")
async def clear_all_documents(x_api_key: Optional[str] = Header(None)) -> dict:
    """
    Delete ALL documents from the collection.
    Use before re-loading a new dataset.
    """
    # Validate API key
    user_context = await _validate_api_key_internal(x_api_key)

    try:
        tenant_id = user_context["tenant_id"]
        vector_store = _get_vector_store_for_tenant(tenant_id)
        deleted = vector_store.clear_all()
        return {
            "success": True,
            "deleted_count": deleted,
            "message": f"Deleted {deleted} documents",
        }
    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing collection: {str(e)}",
        )


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    x_api_key: Optional[str] = Header(None),
) -> dict:
    """
    Delete a document by ID.

    **Parameters:**
    - `doc_id`: The unique identifier of the document to delete

    **Returns:**
    - `success`: Whether the deletion was successful
    - `message`: Result message
    """
    # Validate API key
    user_context = await _validate_api_key_internal(x_api_key)

    try:
        tenant_id = user_context["tenant_id"]
        vector_store = _get_vector_store_for_tenant(tenant_id)
        success = vector_store.delete_document(doc_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found",
            )

        return {"success": True, "message": f"Document {doc_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document",
        )
