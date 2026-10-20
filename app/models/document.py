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
                "id": "part-001",
                "title": "Charge System",
                "content": "solar panels energy reactor battery charging power recharge fuel cells electricity",
                "keywords": ["energy", "battery", "power"],
                "metadata": {
                    "category": "systems",
                    "state": "idle",
                    "source": "manual-v2",
                    "author": "Engineering Team",
                    "date": "2026-01-15",
                    "custom_field": "priority_high",
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
                        "id": "part-001",
                        "title": "Charge System",
                        "content": "solar panels energy reactor battery charging power recharge fuel cells electricity",
                        "keywords": ["energy", "battery"],
                        "metadata": {"state": "idle"},
                    },
                    {
                        "id": "part-002",
                        "title": "Flight System",
                        "content": "thruster engine propulsion fly speed boost travel navigate rocket jet turbine",
                        "keywords": ["engine", "flight"],
                        "metadata": {"state": "active"},
                    },
                    {
                        "id": "part-003",
                        "title": "Stealth System",
                        "content": "cloak invisibility hide camouflage stealth radar ghost disappear vanish disguise",
                        "keywords": ["cloak", "stealth"],
                        "metadata": {"state": "hidden"},
                    },
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
                "id": "part-001",
                "title": "Charge System",
                "content": "solar panels energy reactor battery charging power recharge fuel cells electricity",
                "keywords": ["energy", "battery", "power"],
                "metadata": {"state": "idle"},
                "score": 0.98,
            }
        }
