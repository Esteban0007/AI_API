"""
Load documents from JSON file and index them in the vector store.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine.store import VectorStore
from app.engine.embedder import Embedder
from app.core.config import get_settings


def load_documents_from_json(json_file: Path):
    """Load documents from a JSON file."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "documents" in data:
        return data["documents"]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("JSON must contain a 'documents' key or be a list of documents")


def main():
    """Main function to load and index documents."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Load documents from JSON and index them")
    parser.add_argument(
        "--file",
        type=str,
        default="data/sample_documents.json",
        help="Path to JSON file containing documents"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing collection before loading"
    )
    
    args = parser.parse_args()
    
    json_file = Path(args.file)
    
    if not json_file.exists():
        print(f"Error: File not found at {json_file}")
        sys.exit(1)
    
    print(f"Loading documents from: {json_file}")
    
    try:
        documents = load_documents_from_json(json_file)
        print(f"Loaded {len(documents)} documents from JSON")
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)
    
    # Initialize vector store
    embedder = Embedder()
    vector_store = VectorStore(embedder=embedder)
    
    # Clear existing data if requested
    if args.clear:
        print("Clearing existing collection...")
        vector_store.clear_collection()
    
    # Index documents
    print("Indexing documents...")
    success_count, fail_count = vector_store.add_documents_batch(documents)
    
    # Print results
    print(f"\nIndexing complete!")
    print(f"Successfully indexed: {success_count} documents")
    if fail_count > 0:
        print(f"Failed to index: {fail_count} documents")
    
    # Print collection stats
    stats = vector_store.get_collection_stats()
    print(f"\nCollection Statistics:")
    print(f"  Total documents: {stats.get('document_count', 0)}")
    print(f"  Embedding dimension: {stats.get('embedding_dimension', 0)}")
    print(f"  Model: {stats.get('model', 'Unknown')}")


if __name__ == "__main__":
    main()
