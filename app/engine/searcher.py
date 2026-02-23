"""
Search engine with cross-encoder re-ranking for improved relevance.
"""

import logging
from typing import List, Dict, Tuple
import re
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
            # Step 1: Exact title matches (hybrid ranking)
            exact_title_matches = self.vector_store.get_exact_title_matches(query)
            exact_ids = {doc["id"] for doc in exact_title_matches}

            # Step 2: Fast title token matching (for partial title queries)
            token_title_matches = self.vector_store.get_title_token_matches(query)
            exact_ids.update(doc["id"] for doc in token_title_matches)

            # Step 3: Generate query embedding
            query_embedding = self.embedder.embed_text(query)

            # Step 4: Vector search to get candidates (with optional filters)
            # Use smaller candidate pool - exact/token matches reduce need for semantic search
            candidate_k = min(20, self.rerank_top_k * 2)  # Max 20 candidates
            candidates = self.vector_store.search(
                query_embedding, top_k=candidate_k, filters=filters
            )

            # Remove duplicates already matched by exact title
            if exact_ids:
                candidates = [c for c in candidates if c["id"] not in exact_ids]

            # Prepare final results
            results = []

            # Add exact matches with score 1.0
            if exact_title_matches:
                for match in exact_title_matches:
                    results.append(
                        {
                            "id": match["id"],
                            "title": match["metadata"].get("title", ""),
                            "score": 1.0,
                            "metadata": match["metadata"],
                            "content": match["content"] if include_content else None,
                        }
                    )

            # Add token matches with score 0.95
            if token_title_matches:
                for match in token_title_matches:
                    results.append(
                        {
                            "id": match["id"],
                            "title": match["metadata"].get("title", ""),
                            "score": 0.95,
                            "metadata": match["metadata"],
                            "content": match["content"] if include_content else None,
                        }
                    )

            # Only use cross-encoder re-ranking if we need more results (performance optimization)
            final_top_k = top_k or self.rerank_top_k
            if len(results) < final_top_k and candidates:
                ranked_candidates = self._rerank_results(
                    query, candidates, include_content
                )
                results.extend(ranked_candidates)

            # Step 5: Apply top_k limit
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
                title = candidate["metadata"].get("title", "")
                bonus = self._title_match_bonus(query, title)
                final_score = float(score) + bonus
                if final_score > 1.0:
                    final_score = 1.0
                result = {
                    "id": candidate["id"],
                    "title": title,
                    "score": final_score,
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

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for title matching."""
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _title_match_bonus(self, query: str, title: str) -> float:
        """
        Compute a bonus score for strong title matches.

        Strategy (hybrid ranking):
        - Exact normalized match: +0.40
        - Query substring in title or title in query: +0.25
        - All query tokens contained in title: +0.15
        """
        nq = self._normalize_text(query)
        nt = self._normalize_text(title)

        if not nq or not nt:
            return 0.0

        if nq == nt:
            return 0.40

        if nq in nt or nt in nq:
            return 0.25

        q_tokens = nq.split(" ")
        t_tokens = set(nt.split(" "))
        if q_tokens and all(token in t_tokens for token in q_tokens):
            return 0.15

        return 0.0

    def get_collection_stats(self) -> Dict:
        """Get statistics about the search engine."""
        return self.vector_store.get_collection_stats()


@lru_cache(maxsize=4)
def get_cross_encoder(model_name: str) -> CrossEncoder:
    """Shared cross-encoder instance to avoid reloading per tenant."""
    return CrossEncoder(model_name)
