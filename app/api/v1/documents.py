"""
API endpoints for document management.
"""
from fastapi import APIRouter, HTTPException, status, Depends
import logging
from typing import List

from ...models.document import DocumentCreate, DocumentBatch, DocumentResponse
from ...models.search import DocumentUploadResponse
from ...core.security import validate_api_key
from ...engine.store import VectorStore
from ...engine.embedder import Embedder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

# Global instances
embedder = Embedder()
vector_store = VectorStore(embedder=embedder)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    batch: DocumentBatch,
    api_key: str = Depends(validate_api_key)
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
    try:
        if not batch.documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty document batch"
            )
        
        logger.info(f"Uploading batch of {len(batch.documents)} documents")
        
        # Prepare documents for batch upload
        docs_to_upload = []
        for doc in batch.documents:
            docs_to_upload.append({
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "keywords": doc.keywords or [],
                "metadata": {
                    "category": doc.metadata.category if doc.metadata else None,
                    "language": doc.metadata.language if doc.metadata else "es",
                    "source": doc.metadata.source if doc.metadata else None,
                    "metadata_full": doc.metadata.dict() if doc.metadata else {}
                }
            })
        
        # Upload to vector store
        success_count, fail_count = vector_store.add_documents_batch(docs_to_upload)
        
        return DocumentUploadResponse(
            success=fail_count == 0,
            message=f"Successfully uploaded {success_count} documents" if fail_count == 0 else f"Partial upload: {success_count} succeeded, {fail_count} failed",
            uploaded_count=success_count,
            failed_count=fail_count
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading documents: {str(e)}"
        )


@router.get("/stats")
async def get_stats(api_key: str = Depends(validate_api_key)) -> dict:
    """
    Get statistics about the document collection.
    
    **Returns:**
    - `collection_name`: Name of the vector collection
    - `document_count`: Total number of indexed documents
    - `embedding_dimension`: Dimension of embeddings
    - `model`: Model used for embeddings
    """
    try:
        stats = vector_store.get_collection_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    api_key: str = Depends(validate_api_key)
) -> dict:
    """
    Delete a document by ID.
    
    **Parameters:**
    - `doc_id`: The unique identifier of the document to delete
    
    **Returns:**
    - `success`: Whether the deletion was successful
    - `message`: Result message
    """
    try:
        success = vector_store.delete_document(doc_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Document {doc_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )
