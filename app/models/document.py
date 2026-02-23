"""
Document models for the API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentCreate(BaseModel):
    """Document creation request model."""

    id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content for embedding")
    keywords: Optional[List[str]] = Field(
        None, description="Optional keywords for filtering"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata - can contain any fields (category, language, source, author, date, etc.)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc-001",
                "title": "Machine Learning Basics",
                "content": "Machine learning is a subset of artificial intelligence...",
                "keywords": ["ml", "ai", "learning"],
                "metadata": {
                    "category": "tutorial",
                    "language": "es",
                    "source": "https://example.com/ml-basics",
                    "author": "John Doe",
                    "date": "2024-01-15",
                    "custom_field": "any_value",
                },
            }
        }


class DocumentBatch(BaseModel):
    """Batch of documents for upload."""

    documents: List[DocumentCreate] = Field(
        ..., description="List of documents to upload"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "doc-001",
                        "title": "Title 1",
                        "content": "Content 1...",
                        "metadata": {},
                    }
                ]
            }
        }


class DocumentResponse(BaseModel):
    """Document response model."""

    id: str
    title: str
    content: Optional[str] = None  # May be excluded for privacy
    keywords: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None  # Search relevance score

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc-001",
                "title": "Machine Learning Basics",
                "content": "Machine learning is...",
                "keywords": ["ml", "ai"],
                "metadata": {},
                "score": 0.94,
            }
        }
