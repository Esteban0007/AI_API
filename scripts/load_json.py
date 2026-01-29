#!/usr/bin/env python3
"""
Script to load documents from a JSON file into the vector database.

Usage:
    python scripts/load_json.py path/to/documents.json
"""
import json
import logging
import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine.embedder import Embedder
from app.engine.store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> list:
    """
    Load and validate JSON documents from file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of document dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Support both direct list and dict with 'documents' key
        documents = data if isinstance(data, list) else data.get('documents', [])
        
        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents
    
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        sys.exit(1)


def validate_document(doc: dict) -> bool:
    """
    Validate document structure.
    
    Args:
        doc: Document dictionary
        
    Returns:
        True if valid
    """
    required_fields = ['id', 'title', 'content']
    
    for field in required_fields:
        if field not in doc:
            logger.warning(f"Missing required field '{field}' in document {doc.get('id', 'unknown')}")
            return False
    
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Load JSON documents into vector store")
    parser.add_argument(
        "file_path",
        type=str,
        help="Path to JSON file containing documents",
    )
    parser.add_argument(
        "--tenant",
        type=str,
        default="admin",
        help="Tenant ID (default: admin)",
    )
    args = parser.parse_args()

    file_path = args.file_path
    
    logger.info(f"Starting document loading process...")
    logger.info(f"File: {file_path}")
    
    # Load documents
    documents = load_json_file(file_path)
    
    # Validate documents
    valid_docs = []
    for doc in documents:
        if validate_document(doc):
            valid_docs.append(doc)
    
    if not valid_docs:
        logger.error("No valid documents found")
        sys.exit(1)
    
    logger.info(f"Valid documents: {len(valid_docs)}/{len(documents)}")
    
    # Initialize vector store
    logger.info("Initializing vector store...")
    embedder = Embedder()
    vector_store = VectorStore(embedder=embedder, tenant_id=args.tenant)
    
    # Upload documents
    logger.info(f"Uploading {len(valid_docs)} documents...")
    success_count, fail_count = vector_store.add_documents_batch(valid_docs)
    
    # Report results
    logger.info("=" * 50)
    logger.info("Upload Complete!")
    logger.info(f"Successfully uploaded: {success_count}")
    logger.info(f"Failed uploads: {fail_count}")
    
    # Print stats
    stats = vector_store.get_collection_stats()
    logger.info("=" * 50)
    logger.info("Collection Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("=" * 50)
    logger.info("Document loading completed successfully!")


if __name__ == "__main__":
    main()
