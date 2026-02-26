"""
Search engine with cross-encoder re-ranking for improved relevance.
Optimized for multilingual semantic search with early exit and advanced normalization.
"""

import logging
from typing import List, Dict, Tuple, Optional
import re
import numpy as np
import unicodedata
from sentence_transformers import CrossEncoder
from time import time
from functools import lru_cache

from .embedder import Embedder
from .store import VectorStore
from ..core.config import get_settings

logger = logging.getLogger(__name__)

# Configuration constants
EARLY_EXIT_THRESHOLD = 0.92  # Skip re-ranking if vector similarity > this
MIN_CANDIDATES_FOR_RERANK = 3  # Don't re-rank if fewer candidates
MAX_RERANK_CANDIDATES = 10  # Re-rank only top N candidates
TITLE_MATCH_BONUS = 0.05  # Reduced bonus for title containment match (was 0.25)


class SearchEngine:
    """
    Semantic search engine combining vector similarity with cross-encoder re-ranking.

    Features:
    - Hybrid search: exact match -> token matching -> semantic search
    - Early exit optimization: skip re-ranking if similarity > 0.92
    - Multilingual normalization using unicodedata (NFD)
    - Cross-encoder re-ranking only for ambiguous results
    - Title match bonus scoring
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
            cross_encoder: CrossEncoder instance for re-ranking
        """
        settings = get_settings()
        self.vector_store = vector_store or VectorStore()
        self.embedder = embedder or self.vector_store.embedder
        self.top_k = settings.TOP_K
        self.rerank_top_k = settings.RERANK_TOP_K

        # Load cross-encoder for re-ranking (single instance shared across searches)
        logger.info(f"Loading cross-encoder model: {settings.RERANK_MODEL}")
        try:
            self.cross_encoder = cross_encoder or get_cross_encoder(
                settings.RERANK_MODEL
            )
            logger.info("Cross-encoder loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load cross-encoder: {e}")
            raise

        # Performance metrics
        self.early_exit_count = 0
        self.rerank_count = 0

    def search(
        self,
        query: str,
        top_k: int = None,
        filters: Dict = None,
        include_content: bool = True,
    ) -> Tuple[List[Dict], float]:
        """
        Perform semantic search with intelligent re-ranking pipeline.

        Pipeline:
        1. Exact title matching (no embedding needed)
        2. Token-based title matching (fast, no embedding)
        3. Semantic search with vector similarity
        4. Early exit if similarity > 0.92 (skip re-ranking)
        5. Cross-encoder re-ranking for ambiguous results

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
            final_top_k = top_k or self.rerank_top_k

            # Step 1: Exact title matches (fastest - avoid embeddings entirely)
            exact_title_matches = self.vector_store.get_exact_title_matches(query)
            if exact_title_matches:
                results = []
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

                execution_time = (time() - start_time) * 1000
                logger.info(
                    f"Fast path (exact title): '{query}' completed in {execution_time:.2f}ms "
                    f"(found {len(results)} exact matches)"
                )
                return results[:final_top_k], execution_time

            exact_ids = set()

            # Step 2: Fast title token matching (collect IDs only, don't assign fixed score)
            # Token matches will get their score from semantic search instead
            token_title_matches = self.vector_store.get_title_token_matches(query)
            token_match_ids = {doc["id"] for doc in token_title_matches}
            exact_ids.update(token_match_ids)

            # Prepare results list
            results = []

            # Step 3: Generate query embedding (always - semantic score is ground truth)
            if hasattr(self.embedder, "embed_query"):
                query_embedding = self.embedder.embed_query(query)
            else:
                query_embedding = self.embedder.embed_text(query)

            # Step 4: Vector search to get candidates (includes token match IDs too)
            candidate_k = max(MAX_RERANK_CANDIDATES, final_top_k * 2)
            candidates = self.vector_store.search(
                query_embedding, top_k=candidate_k, filters=filters
            )

            # Remove only exact title matches (score=1.0 already added above)
            candidates = [c for c in candidates if c["id"] not in exact_ids]

            # Step 5: Apply early exit optimization
            # If top candidate has similarity > threshold, skip re-ranking
            high_confidence_results = []
            low_confidence_candidates = []

            for candidate in candidates:
                similarity = candidate["similarity_score"]

                # Small bonus for token title matches - only if semantically relevant
                if candidate["id"] in token_match_ids:
                    similarity = min(similarity + TITLE_MATCH_BONUS, 0.99)

                # Early exit: high confidence candidates skip re-ranking
                if similarity > EARLY_EXIT_THRESHOLD:
                    high_confidence_results.append(
                        {
                            "id": candidate["id"],
                            "title": candidate["metadata"].get("title", ""),
                            "score": float(similarity),
                            "metadata": candidate["metadata"],
                            "content": (
                                candidate["content"] if include_content else None
                            ),
                        }
                    )
                    self.early_exit_count += 1
                else:
                    # Collect low-confidence candidates for re-ranking
                    low_confidence_candidates.append(candidate)

            # Add high-confidence results (bypassed re-ranking)
            results.extend(high_confidence_results)

            # Step 6: Re-rank low-confidence candidates if needed
            if (
                len(results) < final_top_k
                and low_confidence_candidates
                and len(low_confidence_candidates) >= MIN_CANDIDATES_FOR_RERANK
            ):
                reranked = self._rerank_results(
                    query,
                    low_confidence_candidates[:MAX_RERANK_CANDIDATES],
                    include_content,
                )
                results.extend(reranked)
                self.rerank_count += 1
            elif low_confidence_candidates:
                # Not enough candidates for re-ranking, add as-is
                for candidate in low_confidence_candidates[
                    : final_top_k - len(results)
                ]:
                    results.append(
                        {
                            "id": candidate["id"],
                            "title": candidate["metadata"].get("title", ""),
                            "score": float(candidate["similarity_score"]),
                            "metadata": candidate["metadata"],
                            "content": (
                                candidate["content"] if include_content else None
                            ),
                        }
                    )

            # Apply final top_k limit
            results = results[:final_top_k]

            execution_time = (time() - start_time) * 1000
            logger.info(
                f"Search '{query}' completed in {execution_time:.2f}ms. "
                f"Found {len(results)} results (early_exits: {self.early_exit_count}, "
                f"rerankings: {self.rerank_count})"
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
        Only called for low-confidence candidates (similarity <= 0.92).

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

            # Get cross-encoder scores (raw logits)
            cross_scores = self.cross_encoder.predict(query_doc_pairs)

            # Normalize scores to 0-1 range using sigmoid
            reranked_scores = self._sigmoid(cross_scores)

            # Create results with enhanced scoring
            results = []
            for candidate, cross_score in zip(candidates, reranked_scores):
                title = candidate["metadata"].get("title", "")

                # Calculate title match bonus (multilingual normalized)
                title_bonus = self._title_match_bonus(query, title)

                # Combine cross-encoder score with title bonus
                final_score = float(cross_score) + title_bonus

                # Cap at 1.0
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
        Apply sigmoid function to normalize cross-encoder scores to [0, 1].

        Formula: sigmoid(x) = 1 / (1 + e^(-x))

        This converts raw logits from the cross-encoder into interpretable
        probability-like scores.

        Args:
            x: Input array of raw scores

        Returns:
            Sigmoid-normalized array in range [0, 1]
        """
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def _normalize_text_multilingual(text: str) -> str:
        """
        Normalize text for multilingual title matching using unicodedata (NFD).

        This approach:
        - Removes accents and diacritics (é -> e, ñ -> n, etc.)
        - Converts to lowercase
        - Removes special characters and punctuation
        - Normalizes whitespace
        - Preserves word boundaries for better matching

        Examples:
        - "Acción Man" -> "accion man"
        - "Léon: The Professional" -> "leon the professional"
        - "Café de los Ángeles" -> "cafe de los angeles"

        Args:
            text: Raw text to normalize

        Returns:
            Normalized text suitable for multilingual matching
        """
        if not text:
            return ""

        # Step 1: NFD normalization (decompose accented characters)
        # é (U+00E9) becomes e (U+0065) + ´ (U+0301)
        text = unicodedata.normalize("NFD", text)

        # Step 2: Remove combining marks (the diacritics)
        # Keep only base characters
        text = "".join(
            char
            for char in text
            if unicodedata.category(char) != "Mn"  # Mn = Mark, nonspacing
        )

        # Step 3: Convert to lowercase
        text = text.lower()

        # Step 4: Remove special characters but keep spaces
        # This regex keeps alphanumeric and spaces
        text = re.sub(r"[^a-z0-9\s]", " ", text)

        # Step 5: Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _title_match_bonus(self, query: str, title: str) -> float:
        """
        Compute bonus score for strong title matches using multilingual normalization.

        Scoring strategy:
        - Exact normalized match: +0.30
        - Query is substring in title (normalized): +0.25
        - Query in title (case-insensitive): +0.20
        - Title starts with query (normalized): +0.22
        - All query tokens in title tokens: +0.10

        Args:
            query: User search query
            title: Document title

        Returns:
            Bonus score (0.0 - 0.30)
        """
        # Normalize using multilingual approach
        nq = self._normalize_text_multilingual(query)
        nt = self._normalize_text_multilingual(title)

        if not nq or not nt:
            return 0.0

        # Exact match on normalized text
        if nq == nt:
            return 0.30

        # Query is substring of title (normalized)
        # e.g., "woman" in "a woman scorned"
        if nq in nt:
            return TITLE_MATCH_BONUS

        # Title starts with query (normalized)
        # e.g., query "lion king" matches title "The Lion King Returns"
        if nt.startswith(nq):
            return 0.22

        # Query substring in original title (case-insensitive)
        # e.g., "Avatar" in "AVATAR: The Last Airbender"
        if query.lower() in title.lower():
            return 0.20

        # All query tokens present in title tokens
        # e.g., query "star wars" tokens ["star", "wars"] match title "Star Wars Episode IV"
        q_tokens = nq.split()
        t_tokens = set(nt.split())
        if q_tokens and all(token in t_tokens for token in q_tokens):
            return 0.10

        return 0.0

    def get_collection_stats(self) -> Dict:
        """Get statistics about the search engine."""
        return self.vector_store.get_collection_stats()


@lru_cache(maxsize=4)
def get_cross_encoder(model_name: str) -> CrossEncoder:
    """Shared cross-encoder instance to avoid reloading per tenant."""
    return CrossEncoder(model_name)
