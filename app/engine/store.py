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

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages vector storage and retrieval using Chroma.
    Handles document persistence and similarity search.
    """
    
    def __init__(self, embedder: Embedder = None, persist_dir: str = None):
        """
        Initialize the vector store.
        
        Args:
            embedder: Embedder instance for generating embeddings
            persist_dir: Directory for persisting Chroma data
        """
        settings = get_settings()
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self.embedder = embedder or Embedder()
        
        # Ensure persist directory exists
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client with persistence
        logger.info(f"Initializing Chroma with persist directory: {self.persist_dir}")
        try:
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Vector store initialized. Collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
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
            # Generate embedding
            embedding = self.embedder.embed_text(content)
            
            # Prepare metadata
            chroma_metadata = {
                "title": metadata.get("title", ""),
                "doc_id": doc_id,
            }
            
            # Add optional metadata fields
            if "category" in metadata:
                chroma_metadata["category"] = metadata["category"]
            if "language" in metadata:
                chroma_metadata["language"] = metadata["language"]
            if "source" in metadata:
                chroma_metadata["source"] = metadata["source"]
            
            # Store the full document JSON for later retrieval
            full_document = {
                "id": doc_id,
                "title": metadata.get("title", ""),
                "content": content,
                "keywords": metadata.get("keywords", []),
                "metadata": metadata.get("metadata_full", {})
            }
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding.tolist()],
                documents=[content],
                metadatas=[chroma_metadata],
                uris=[json.dumps(full_document)]  # Store full doc as URI
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
            # Generate all embeddings at once
            for doc in documents:
                doc_ids.append(doc["id"])
                contents.append(doc["content"])
            
            embeddings_list = self.embedder.embed_texts(contents)
            embeddings = [e.tolist() for e in embeddings_list]
            
            # Prepare metadata
            for doc, emb in zip(documents, embeddings):
                metadata = {
                    "title": doc.get("title", ""),
                    "doc_id": doc["id"],
                }
                
                if "category" in doc.get("metadata", {}):
                    metadata["category"] = doc["metadata"]["category"]
                if "language" in doc.get("metadata", {}):
                    metadata["language"] = doc["metadata"]["language"]
                if "source" in doc.get("metadata", {}):
                    metadata["source"] = doc["metadata"]["source"]
                
                metadatas.append(metadata)
                
                full_documents.append({
                    "id": doc["id"],
                    "title": doc.get("title", ""),
                    "content": doc["content"],
                    "keywords": doc.get("keywords", []),
                    "metadata": doc.get("metadata", {})
                })
            
            # Add batch to collection
            self.collection.add(
                ids=doc_ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                uris=[json.dumps(doc) for doc in full_documents]
            )
            
            success_count = len(documents)
            logger.info(f"Batch upload completed: {success_count} documents")
            
        except Exception as e:
            logger.error(f"Error in batch upload: {e}")
            failure_count = len(documents)
        
        return success_count, failure_count
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return
            
        Returns:
            List of result dicts with id, content, distance, metadata
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=["distances", "documents", "metadatas"]
            )
            
            # Process results
            search_results = []
            if results["ids"] and len(results["ids"]) > 0:
                for idx, doc_id in enumerate(results["ids"][0]):
                    result = {
                        "id": doc_id,
                        "distance": results["distances"][0][idx],  # Cosine distance
                        "similarity_score": 1 - results["distances"][0][idx],  # Convert to similarity
                        "content": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx]
                    }
                    search_results.append(result)
            
            return search_results
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
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
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if result["ids"] and len(result["ids"]) > 0:
                return {
                    "id": doc_id,
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0]
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
                "model": self.embedder.get_model_name()
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
