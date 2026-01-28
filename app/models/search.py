"""
Search-related models for the API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from .document import DocumentResponse


class SearchQuery(BaseModel):
    """Search query request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query string")
    top_k: Optional[int] = Field(5, ge=1, le=50, description="Number of results to return")
    filters: Optional[dict] = Field(None, description="Optional filters (e.g., category, language)")
    include_content: Optional[bool] = Field(True, description="Include document content in results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How does machine learning work?",
                "top_k": 5,
                "filters": {"language": "es"},
                "include_content": True
            }
        }


class SearchResult(BaseModel):
    """Individual search result."""
    id: str
    title: str
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    content: Optional[str] = None
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc-001",
                "title": "Machine Learning Basics",
                "score": 0.94,
                "content": "Machine learning is...",
                "metadata": {"category": "tutorial"}
            }
        }


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    total_results: int
    results: List[SearchResult] = Field(..., description="Ranked search results")
    execution_time_ms: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "How does machine learning work?",
                "total_results": 3,
                "results": [
                    {
                        "id": "doc-001",
                        "title": "ML Basics",
                        "score": 0.94,
                        "content": "..."
                    }
                ],
                "execution_time_ms": 125.5
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response for document upload operation."""
    success: bool
    message: str
    uploaded_count: int
    failed_count: int
    details: Optional[List[dict]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Documents uploaded successfully",
                "uploaded_count": 10,
                "failed_count": 0
            }
        }
