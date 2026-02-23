"""
Search engine with cross-encoder re-ranking for improved relevance.
"""

import logging
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import CrossEncoder
from time import time
from functools import lru_cache

from .embedder import Embedder
from .store import VectorStore
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Semantic search engine combining vector similarity with cross-encoder re-ranking.
    """

    def __init__(
        self,
        vector_store: VectorStore = None,
        embedder: Embedder = None,
        cross_encoder: CrossEncoder = None,
    ):
        """
        Initialize search engine.

        Args:
            vector_store: VectorStore instance
            embedder: Embedder instance
        """
        settings = get_settings()
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or self.vector_store.embedder
        self.top_k = settings.TOP_K
        self.rerank_top_k = settings.RERANK_TOP_K

        # Load cross-encoder for re-ranking
        logger.info(f"Loading cross-encoder model: {settings.RERANK_MODEL}")
        try:
            self.cross_encoder = cross_encoder or get_cross_encoder(
                settings.RERANK_MODEL
            )
            logger.info("Cross-encoder loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load cross-encoder: {e}")
            raise

    def search(
        self,
        query: str,
        top_k: int = None,
        filters: Dict = None,
        include_content: bool = True,
    ) -> Tuple[List[Dict], float]:
        """
        Perform semantic search with re-ranking.

        Pipeline:
        1. Convert query to embedding
        2. Retrieve top_k candidates using vector similarity
        3. Re-rank candidates using cross-encoder
        4. Return top results with relevance scores

        Args:
            query: Search query string
            top_k: Number of results to return (overrides config)
            filters: Optional metadata filters
            include_content: Whether to include document content in results

        Returns:
            Tuple of (results_list, execution_time_ms)
        """
        start_time = time()

        if not query or not isinstance(query, str):
            logger.error("Invalid query")
            return [], 0

        try:
            # Step 1: Generate query embedding
            query_embedding = self.embedder.embed_text(query)

            # Step 2: Vector search to get candidates (with optional filters)
            candidates = self.vector_store.search(
                query_embedding, top_k=self.rerank_top_k, filters=filters
            )

            if not candidates:
                logger.info(f"No candidates found for query: {query}")
                execution_time = (time() - start_time) * 1000
                return [], execution_time

            # Step 3: Re-rank using cross-encoder
            results = self._rerank_results(query, candidates, include_content)

            # Step 4: Apply top_k limit
            final_top_k = top_k or self.rerank_top_k
            results = results[:final_top_k]

            execution_time = (time() - start_time) * 1000
            logger.info(
                f"Search completed for '{query}' in {execution_time:.2f}ms. Found {len(results)} results"
            )

            return results, execution_time

        except Exception as e:
            logger.error(f"Error during search: {e}")
            execution_time = (time() - start_time) * 1000
            return [], execution_time

    def _rerank_results(
        self, query: str, candidates: List[Dict], include_content: bool = True
    ) -> List[Dict]:
        """
        Re-rank candidate documents using cross-encoder.

        Args:
            query: Search query
            candidates: List of candidate documents from vector search
            include_content: Whether to include content in results

        Returns:
            Re-ranked list of results with relevance scores
        """
        if not candidates:
            return []

        try:
            # Prepare pairs of (query, document) for cross-encoder
            query_doc_pairs = [
                [query, candidate["content"]] for candidate in candidates
            ]

            # Get cross-encoder scores
            cross_scores = self.cross_encoder.predict(query_doc_pairs)

            # Normalize scores to 0-1 range using sigmoid
            reranked_scores = self._sigmoid(cross_scores)

            # Create results with scores
            results = []
            for candidate, score in zip(candidates, reranked_scores):
                result = {
                    "id": candidate["id"],
                    "title": candidate["metadata"].get("title", ""),
                    "score": float(score),
                    "metadata": candidate["metadata"],
                }

                if include_content:
                    result["content"] = candidate["content"]

                results.append(result)

            # Sort by relevance score (descending)
            results.sort(key=lambda x: x["score"], reverse=True)

            return results

        except Exception as e:
            logger.error(f"Error during re-ranking: {e}")
            # Fallback to vector similarity scores if re-ranking fails
            return [
                {
                    "id": c["id"],
                    "title": c["metadata"].get("title", ""),
                    "score": float(c["similarity_score"]),
                    "metadata": c["metadata"],
                    "content": c["content"] if include_content else None,
                }
                for c in candidates
            ]

    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        """
        Apply sigmoid function to normalize cross-encoder scores.

        Args:
            x: Input array

        Returns:
            Sigmoid-normalized array
        """
        return 1 / (1 + np.exp(-x))

    def get_collection_stats(self) -> Dict:
        """Get statistics about the search engine."""
        return self.vector_store.get_collection_stats()


@lru_cache(maxsize=4)
def get_cross_encoder(model_name: str) -> CrossEncoder:
    """Shared cross-encoder instance to avoid reloading per tenant."""
    return CrossEncoder(model_name)
