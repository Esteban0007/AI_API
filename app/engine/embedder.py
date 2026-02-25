"""
Embedding generation module using HuggingFace sentence-transformers.
"""

import logging
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

try:
    import onnxruntime as ort
except Exception:  # pragma: no cover - optional dependency
    ort = None
from ..core.config import get_settings

logger = logging.getLogger(__name__)


class Embedder:
    """
    Handles embedding generation using sentence-transformers.
    Supports caching and batch processing.
    """

    def __init__(self, model_name: str = None):
        """
        Initialize the embedder with a specific model.

        Args:
            model_name: HuggingFace model name. If None, uses config default.
        """
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.embedding_dim = settings.EMBEDDING_DIMENSION
        self.use_onnx = settings.EMBEDDING_USE_ONNX
        self.onnx_dir = settings.EMBEDDING_ONNX_DIR
        self.query_prefix = "Represent this query for retrieval: "
        self._is_onnx = False

        logger.info(f"Loading embedding model: {self.model_name}")
        if self.use_onnx and ort is not None:
            try:
                if not self.onnx_dir:
                    raise ValueError(
                        "EMBEDDING_ONNX_DIR is required when EMBEDDING_USE_ONNX is true"
                    )
                self.tokenizer = AutoTokenizer.from_pretrained(self.onnx_dir)
                model_path = f"{self.onnx_dir}/model.onnx"
                self.onnx_session = ort.InferenceSession(
                    model_path, providers=["CPUExecutionProvider"]
                )
                self.onnx_input_names = {i.name for i in self.onnx_session.get_inputs()}
                self.onnx_output_names = [
                    o.name for o in self.onnx_session.get_outputs()
                ]
                self._is_onnx = True
                logger.info(
                    f"ONNX embedding model loaded successfully. Dimension: {self.embedding_dim}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to load ONNX model, falling back to sentence-transformers: {e}"
                )
                self.model = SentenceTransformer(self.model_name)
        else:
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(
                    f"Embedding model loaded successfully. Dimension: {self.embedding_dim}"
                )
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            numpy array of shape (embedding_dim,)
        """
        if not text or not isinstance(text, str):
            raise ValueError("Input must be a non-empty string")

        # Clean and truncate text if needed
        text = text.strip()
        if len(text) > 10000:
            logger.warning(f"Text truncated from {len(text)} to 10000 characters")
            text = text[:10000]

        try:
            if self._is_onnx:
                return self.embed_texts([text])[0]

            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query, applying model-specific prompt.

        Args:
            query: User search query

        Returns:
            numpy array of shape (embedding_dim,)
        """
        if not query or not isinstance(query, str):
            raise ValueError("Input must be a non-empty string")

        if "snowflake-arctic-embed" in self.model_name and not query.startswith(
            self.query_prefix
        ):
            query = f"{self.query_prefix}{query}"

        return self.embed_text(query)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of numpy arrays
        """
        if not texts:
            return []

        if not all(isinstance(t, str) for t in texts):
            raise ValueError("All inputs must be strings")

        # Clean texts
        texts = [t.strip()[:10000] for t in texts]

        try:
            if self._is_onnx:
                return self._embed_texts_onnx(texts)

            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            return [e.astype(np.float32) for e in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings for batch: {e}")
            raise

    def _embed_texts_onnx(self, texts: List[str]) -> List[np.ndarray]:
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="np",
        )

        if "token_type_ids" in inputs and "token_type_ids" not in self.onnx_input_names:
            inputs.pop("token_type_ids")

        onnx_inputs = {k: v for k, v in inputs.items() if k in self.onnx_input_names}
        outputs = self.onnx_session.run(self.onnx_output_names, onnx_inputs)
        outputs_map = dict(zip(self.onnx_output_names, outputs))

        if "sentence_embedding" in outputs_map:
            sentence_embeddings = outputs_map["sentence_embedding"]
        elif "token_embeddings" in outputs_map:
            token_embeddings = outputs_map["token_embeddings"]
            mask = inputs["attention_mask"][..., None].astype(np.float32)
            sentence_embeddings = (token_embeddings * mask).sum(1) / np.clip(
                mask.sum(1), a_min=1e-9, a_max=None
            )
        else:
            raise ValueError("ONNX model did not return sentence embeddings")

        return [e.astype(np.float32) for e in sentence_embeddings]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.embedding_dim

    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model_name
