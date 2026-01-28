"""
Embedding generation module using HuggingFace sentence-transformers.
"""
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
import logging
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
        
        logger.info(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded successfully. Dimension: {self.embedding_dim}")
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
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
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
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return [e.astype(np.float32) for e in embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings for batch: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.embedding_dim
    
    def get_model_name(self) -> str:
        """Get the model name being used."""
        return self.model_name
