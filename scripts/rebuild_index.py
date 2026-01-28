#!/usr/bin/env python3
"""
Script to rebuild the search index (re-generate all embeddings).

This is useful when:
- Changing the embedding model
- Updating embedding parameters
- Recovering from data corruption

Warning: This will delete all existing embeddings and regenerate them.

Usage:
    python scripts/rebuild_index.py --source documents.json
"""
import argparse
import logging
import sys
import json
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine.embedder import Embedder
from app.engine.store import VectorStore
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backup_database(db_path: str) -> str:
    """
    Create a backup of the existing database.
    
    Args:
        db_path: Path to the database directory
        
    Returns:
        Path to backup directory
    """
    if not Path(db_path).exists():
        return None
    
    backup_path = f"{db_path}.backup"
    logger.info(f"Creating backup at {backup_path}...")
    
    if Path(backup_path).exists():
        shutil.rmtree(backup_path)
    
    shutil.copytree(db_path, backup_path)
    logger.info(f"Backup created successfully")
    return backup_path


def clear_database(db_path: str) -> bool:
    """
    Clear the existing database.
    
    Args:
        db_path: Path to the database directory
        
    Returns:
        True if successful
    """
    if not Path(db_path).exists():
        logger.info("Database does not exist, skipping clear")
        return True
    
    logger.info(f"Clearing database at {db_path}...")
    try:
        shutil.rmtree(db_path)
        logger.info("Database cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return False


def load_documents(source_file: str) -> list:
    """
    Load documents from source file.
    
    Args:
        source_file: Path to JSON file with documents
        
    Returns:
        List of documents
    """
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = data if isinstance(data, list) else data.get('documents', [])
        logger.info(f"Loaded {len(documents)} documents from {source_file}")
        return documents
    
    except FileNotFoundError:
        logger.error(f"Source file not found: {source_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Rebuild the search index from documents"
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to JSON file containing documents"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before rebuilding (default: True)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation"
    )
    
    args = parser.parse_args()
    
    settings = get_settings()
    db_path = settings.CHROMA_PERSIST_DIRECTORY
    
    logger.info("=" * 60)
    logger.info("Index Rebuild Process Started")
    logger.info("=" * 60)
    
    # Backup if requested
    if args.backup and not args.no_backup:
        backup_path = backup_database(db_path)
        if backup_path:
            logger.info(f"Backup location: {backup_path}")
    
    # Clear existing database
    if not clear_database(db_path):
        logger.error("Failed to clear database")
        sys.exit(1)
    
    # Load documents
    documents = load_documents(args.source)
    
    if not documents:
        logger.error("No documents to load")
        sys.exit(1)
    
    # Reinitialize vector store (creates new collection)
    logger.info("Initializing new vector store...")
    embedder = Embedder()
    vector_store = VectorStore(embedder=embedder)
    
    # Rebuild index
    logger.info(f"Rebuilding index with {len(documents)} documents...")
    success_count, fail_count = vector_store.add_documents_batch(documents)
    
    # Report results
    logger.info("=" * 60)
    logger.info("Index Rebuild Complete!")
    logger.info(f"Successfully indexed: {success_count}")
    logger.info(f"Failed indexes: {fail_count}")
    
    # Print stats
    stats = vector_store.get_collection_stats()
    logger.info("=" * 60)
    logger.info("Collection Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("=" * 60)
    logger.info("Index rebuild completed successfully!")


if __name__ == "__main__":
    main()
