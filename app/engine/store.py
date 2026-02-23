"""
Vector database store using Chroma for persistence and fast similarity search.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
import logging
from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path
from ..core.config import get_settings
from .embedder import Embedder
import numpy as np
import re

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages vector storage and retrieval using Chroma.
    Handles document persistence and similarity search.
    """

    _client_by_path: Dict[str, chromadb.PersistentClient] = {}

    def __init__(
        self,
        embedder: Embedder = None,
        persist_dir: str = None,
        collection_name: str = None,
        tenant_id: str = None,
    ):
        """
        Initialize the vector store.

        Args:
            embedder: Embedder instance for generating embeddings
            persist_dir: Directory for persisting Chroma data
        """
        settings = get_settings()
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        self.tenant_id = tenant_id
        if collection_name:
            self.collection_name = collection_name
        elif tenant_id:
            safe_tenant_id = self._sanitize_tenant_id(tenant_id)
            self.collection_name = f"{settings.CHROMA_COLLECTION_NAME}_{safe_tenant_id}"
        else:
            self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.embedder = embedder or Embedder()

        # Ensure persist directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client with persistence
        logger.info(f"Initializing Chroma with persist directory: {self.persist_dir}")
        try:
            self.client = self._get_client(self.persist_dir)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Vector store initialized. Collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    @staticmethod
    def _extract_filterable_metadata(metadata: Dict) -> Dict:
        """
        Extract common filterable fields from metadata for ChromaDB indexing.
        Only extracts fields with simple types (str, int, float, bool).

        Universal fields for any use case.
        """
        filterable = {}

        # Minimal universal field - only language
        common_fields = [
            "language",  # language code or programming language
        ]

        for field in common_fields:
            if field in metadata:
                value = metadata[field]
                # Only add if it's a simple type that ChromaDB can index
                if isinstance(value, (str, int, float, bool)):
                    filterable[field] = value

        return filterable

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize title for exact matching."""
        if not title:
            return ""
        text = title.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def add_document(self, doc_id: str, content: str, metadata: Dict) -> bool:
        """
        Add a single document to the vector store.

        Args:
            doc_id: Unique document identifier
            content: Document content to embed
            metadata: Document metadata (title, category, etc.)

        Returns:
            True if successful
        """
        try:
            # Generate embedding from title + content + keywords
            title = metadata.get("title", "")
            keywords = metadata.get("keywords", [])

            # Build text to embed
            parts = []
            if title:
                parts.append(title)
            parts.append(content)
            if keywords:
                keywords_str = ", ".join(keywords)
                parts.append(f"Keywords: {keywords_str}")

            text_to_embed = "\n\n".join(parts)
            embedding = self.embedder.embed_text(text_to_embed)

            # Prepare metadata - copy all user metadata fields
            chroma_metadata = {
                "title": metadata.get("title", ""),
                "title_normalized": self._normalize_title(metadata.get("title", "")),
                "doc_id": doc_id,
            }
            if self.tenant_id:
                chroma_metadata["tenant_id"] = self.tenant_id

            # Extract filterable fields from metadata
            user_metadata = metadata.get("metadata", {})
            filterable_fields = self._extract_filterable_metadata(user_metadata)
            chroma_metadata.update(filterable_fields)

            # Store the full document JSON for later retrieval
            full_document = {
                "id": doc_id,
                "title": metadata.get("title", ""),
                "content": content,
                "keywords": metadata.get("keywords", []),
                "metadata": metadata.get("metadata", {}),
                "tenant_id": self.tenant_id,
            }

            # Add to collection
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding.tolist()],
                documents=[content],
                metadatas=[chroma_metadata],
                uris=[json.dumps(full_document)],  # Store full doc as URI
            )

            logger.info(f"Document added: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding document {doc_id}: {e}")
            return False

    def add_documents_batch(self, documents: List[Dict]) -> Tuple[int, int]:
        """
        Add multiple documents efficiently.

        Args:
            documents: List of dicts with keys: id, title, content, keywords, metadata

        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0

        # Extract content and metadata
        doc_ids = []
        contents = []
        embeddings = []
        metadatas = []
        full_documents = []

        try:
            # Generate all embeddings at once from title + content + keywords
            for doc in documents:
                doc_ids.append(doc["id"])
                title = doc.get("title", "")
                keywords = doc.get("keywords", [])
                content = doc["content"]

                # Build text to embed
                parts = []
                if title:
                    parts.append(title)
                parts.append(content)
                if keywords:
                    keywords_str = ", ".join(keywords)
                    parts.append(f"Keywords: {keywords_str}")

                text_to_embed = "\n\n".join(parts)
                contents.append(text_to_embed)

            embeddings_list = self.embedder.embed_texts(contents)
            embeddings = [e.tolist() for e in embeddings_list]

            # Prepare metadata
            for doc in documents:
                metadata = {
                    "title": doc.get("title", ""),
                    "title_normalized": self._normalize_title(doc.get("title", "")),
                    "doc_id": doc["id"],
                }
                if self.tenant_id:
                    metadata["tenant_id"] = self.tenant_id

                # Extract filterable fields from metadata
                user_metadata = doc.get("metadata", {})
                filterable_fields = self._extract_filterable_metadata(user_metadata)
                metadata.update(filterable_fields)

                metadatas.append(metadata)

                full_documents.append(
                    {
                        "id": doc["id"],
                        "title": doc.get("title", ""),
                        "content": doc["content"],
                        "keywords": doc.get("keywords", []),
                        "metadata": doc.get("metadata", {}),
                        "tenant_id": self.tenant_id,
                    }
                )

            # Add batch to collection
            self.collection.add(
                ids=doc_ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                uris=[json.dumps(doc) for doc in full_documents],
            )

            success_count = len(documents)
            logger.info(f"Batch upload completed: {success_count} documents")

        except Exception as e:
            logger.error(f"Error in batch upload: {e}")
            failure_count = len(documents)

        return success_count, failure_count

    def search(
        self, query_embedding: np.ndarray, top_k: int = 10, filters: Dict = None
    ) -> List[Dict]:
        """
        Search for similar documents using cosine similarity.

        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"category": "news", "language": "es"})

        Returns:
            List of result dicts with id, content, distance, metadata
        """
        try:
            query_params = {
                "query_embeddings": [query_embedding.tolist()],
                "n_results": top_k,
                "include": ["distances", "documents", "metadatas"],
            }

            # Add filters if provided
            if filters:
                # Build where clause for ChromaDB
                where_clause = {}
                for key, value in filters.items():
                    if value is not None:
                        where_clause[key] = value

                if where_clause:
                    query_params["where"] = where_clause

            results = self.collection.query(**query_params)

            # Process results
            search_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for idx, doc_id in enumerate(results["ids"][0]):
                    result = {
                        "id": doc_id,
                        "distance": results["distances"][0][idx],  # Cosine distance
                        "similarity_score": 1
                        - results["distances"][0][idx],  # Convert to similarity
                        "content": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx],
                    }
                    search_results.append(result)

            return search_results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []

    def get_exact_title_matches(self, title: str) -> List[Dict]:
        """
        Retrieve documents whose title matches the query exactly.

        Args:
            title: Title string to match

        Returns:
            List of result dicts with id, content, metadata
        """
        if not title:
            return []

        results: List[Dict] = []
        seen_ids: set[str] = set()

        try:
            exact = self.collection.get(
                where={"title": title}, include=["documents", "metadatas"]
            )
            if exact.get("ids"):
                for idx, doc_id in enumerate(exact["ids"]):
                    seen_ids.add(doc_id)
                    results.append(
                        {
                            "id": doc_id,
                            "distance": 0.0,
                            "similarity_score": 1.0,
                            "content": exact["documents"][idx],
                            "metadata": exact["metadatas"][idx],
                        }
                    )
        except Exception as e:
            logger.error(f"Error fetching exact title matches: {e}")

        try:
            normalized = self._normalize_title(title)
            if normalized:
                exact_norm = self.collection.get(
                    where={"title_normalized": normalized},
                    include=["documents", "metadatas"],
                )
                if exact_norm.get("ids"):
                    for idx, doc_id in enumerate(exact_norm["ids"]):
                        if doc_id in seen_ids:
                            continue
                        results.append(
                            {
                                "id": doc_id,
                                "distance": 0.0,
                                "similarity_score": 1.0,
                                "content": exact_norm["documents"][idx],
                                "metadata": exact_norm["metadatas"][idx],
                            }
                        )
        except Exception as e:
            logger.error(f"Error fetching normalized title matches: {e}")

        return results

    def get_title_token_matches(self, query: str) -> List[Dict]:
        """
        Fast title token matching for partial title queries.
        Uses token-based matching instead of full embedding.

        Args:
            query: Query string

        Returns:
            List of documents whose title contains query tokens
        """
        if not query:
            return []

        results: List[Dict] = []
        seen_ids: set[str] = set()

        try:
            # Normalize and tokenize
            nq = self._normalize_title(query)
            if not nq:
                return []

            query_tokens = nq.split(" ")

            # Retrieve ALL documents and filter by token match
            all_docs = self.collection.get(include=["documents", "metadatas"])

            if not all_docs.get("ids"):
                return []

            # Score each document by how many tokens match
            scored_docs = []
            for idx, doc_id in enumerate(all_docs["ids"]):
                title = all_docs["metadatas"][idx].get("title", "")
                title_norm = self._normalize_title(title)
                title_tokens = set(title_norm.split(" ")) if title_norm else set()

                # Count matching tokens
                matching_tokens = sum(
                    1 for token in query_tokens if token in title_tokens
                )

                if matching_tokens > 0:
                    score = matching_tokens / len(query_tokens)
                    scored_docs.append(
                        (
                            score,
                            {
                                "id": doc_id,
                                "distance": 0.0,
                                "similarity_score": score,
                                "content": all_docs["documents"][idx],
                                "metadata": all_docs["metadatas"][idx],
                            },
                        )
                    )

            # Sort by score (descending) and return
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            results = [doc for _, doc in scored_docs]

            return results
        except Exception as e:
            logger.error(f"Error in title token matching: {e}")
            return []

    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Retrieve a specific document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document dict or None if not found
        """
        try:
            result = self.collection.get(
                ids=[doc_id], include=["documents", "metadatas"]
            )

            if result["ids"] and len(result["ids"]) > 0:
                return {
                    "id": doc_id,
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
            return None

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.

        Args:
            doc_id: Document identifier

        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Document deleted: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embedding_dimension": self.embedder.get_embedding_dimension(),
                "model": self.embedder.get_model_name(),
                "tenant_id": self.tenant_id,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def clear_collection(self) -> None:
        """Delete all documents in the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection cleared: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection {self.collection_name}: {e}")
            raise

    @classmethod
    def _get_client(cls, persist_dir: str) -> chromadb.PersistentClient:
        if persist_dir not in cls._client_by_path:
            cls._client_by_path[persist_dir] = chromadb.PersistentClient(
                path=persist_dir
            )
        return cls._client_by_path[persist_dir]

    @staticmethod
    def _sanitize_tenant_id(tenant_id: str) -> str:
        cleaned = tenant_id.strip().lower()
        cleaned = re.sub(r"[^a-z0-9_-]", "-", cleaned)
        cleaned = cleaned.strip("-")
        return cleaned[:64] or "default"
