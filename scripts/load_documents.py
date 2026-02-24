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


def improve_document_content(doc: dict) -> dict:
    """
    Restructure document content for better semantic search.

    Converts messy content with newlines/keywords into structured format:
    Title: ...
    Summary: ...
    Director: ...
    Cast: ...
    Genres: ...
    Rating: .../10
    Release Year: ...
    """
    metadata = doc.get("metadata", {})
    title = doc.get("title", "")
    original_content = doc.get("content", "")

    # Extract key fields from metadata
    director = metadata.get("director", "Unknown")
    cast = metadata.get("cast", [])
    genres = metadata.get("genres", [])
    rating = metadata.get("rating", 0)
    release_date = metadata.get("release_date", "")

    # Extract year from release_date (YYYY-MM-DD format)
    release_year = release_date.split("-")[0] if release_date else ""

    # Clean up original content - remove "Title\n\n" prefix if exists
    summary = original_content
    if "\n\n" in summary:
        # Take only the first paragraph (before Keywords)
        summary = summary.split("\n\nKeywords:")[0]
        if summary.startswith(f"{title}\n\n"):
            summary = summary[len(title) + 2 :].strip()

    # Format cast as string
    cast_str = ", ".join(cast) if isinstance(cast, list) else str(cast)
    genres_str = ", ".join(genres) if isinstance(genres, list) else str(genres)

    # Build structured content (without Rating and Keywords - already explained in fields)
    structured_content = f"""Title: {title}

Summary: {summary.strip()}

Director: {director}
Cast: {cast_str}
Genres: {genres_str}
Release Year: {release_year}"""

    # Update document with improved content
    doc["content"] = structured_content

    return doc


def load_documents_from_json(json_file: Path):
    """Load documents from a JSON file."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "documents" in data:
        return data["documents"]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(
            "JSON must contain a 'documents' key or be a list of documents"
        )


def main():
    """Main function to load and index documents."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Load documents from JSON and index them"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="data/sample_documents.json",
        help="Path to JSON file containing documents",
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing collection before loading"
    )
    parser.add_argument(
        "--tenant",
        type=str,
        default="admin",
        help="Tenant ID (default: admin)",
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

        # Improve document content for better semantic search
        print("Improving document content structure...")
        documents = [improve_document_content(doc) for doc in documents]
        print("✓ Document content improved for semantic search")
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit(1)

    # Initialize vector store
    embedder = Embedder()
    vector_store = VectorStore(embedder=embedder, tenant_id=args.tenant)

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
