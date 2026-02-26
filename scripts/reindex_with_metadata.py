#!/usr/bin/env python3
"""
Re-index all existing documents with the new structured embedding format.

This script reads all documents from ChromaDB (using the stored full metadata),
then re-embeds them using the new _build_embed_text() format that includes:
  Title, Summary, Category (genres), Director, Cast, Year Released

This makes actor/director/genre searches work correctly.

Usage:
    python scripts/reindex_with_metadata.py [--dry-run]
"""
import argparse
import logging
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import chromadb
from app.engine.embedder import Embedder
from app.engine.store import VectorStore
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def export_all_docs(db_path: str, collection_name: str) -> list:
    """Read all documents from ChromaDB and reconstruct document dicts."""
    client = chromadb.PersistentClient(path=db_path)
    col = client.get_collection(collection_name)
    total = col.count()
    logger.info(f"Found {total} documents in collection '{collection_name}'")

    # Fetch in batches of 500
    all_docs = []
    batch_size = 500
    offset = 0

    while offset < total:
        results = col.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas", "uris"],
        )
        ids = results["ids"]
        metas = results["metadatas"]
        uris = results.get("uris") or []

        for i, doc_id in enumerate(ids):
            meta = metas[i]

            # Try to reconstruct from URI (full JSON stored at index time)
            full_doc = None
            if uris and i < len(uris) and uris[i]:
                try:
                    full_doc = json.loads(uris[i])
                except Exception:
                    pass

            if full_doc:
                # Use the stored full document
                doc = {
                    "id": full_doc.get("id", doc_id),
                    "title": full_doc.get("title", meta.get("title", "")),
                    "content": full_doc.get("content", ""),
                    "keywords": full_doc.get("keywords", []),
                    "metadata": full_doc.get("metadata", {}),
                }
            else:
                # Fallback: reconstruct from metadata fields
                full_meta_str = meta.get("_full_metadata", "{}")
                try:
                    full_meta = json.loads(full_meta_str)
                except Exception:
                    full_meta = {}

                doc = {
                    "id": doc_id,
                    "title": meta.get("title", ""),
                    "content": (
                        results["documents"][i] if results.get("documents") else ""
                    ),
                    "keywords": [],
                    "metadata": full_meta,
                }

            all_docs.append(doc)
        offset += batch_size
        logger.info(f"  Exported {min(offset, total)}/{total} documents...")

    return all_docs


def main():
    parser = argparse.ArgumentParser(
        description="Re-index documents with enriched embedding format"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show sample output without reindexing"
    )
    args = parser.parse_args()

    settings = get_settings()
    db_path = settings.CHROMA_PERSIST_DIRECTORY

    # Discover collection name
    client = chromadb.PersistentClient(path=db_path)
    cols = client.list_collections()
    if not cols:
        logger.error("No collections found in ChromaDB")
        sys.exit(1)
    collection_name = cols[0].name
    logger.info(f"Using collection: {collection_name}")

    # Export existing docs
    logger.info("Exporting existing documents from ChromaDB...")
    documents = export_all_docs(db_path, collection_name)

    if not documents:
        logger.error("No documents found to reindex")
        sys.exit(1)

    logger.info(f"Total documents to reindex: {len(documents)}")

    # Show sample of what the new embedding text will look like
    sample = documents[0]
    sample_text = VectorStore._build_embed_text(
        sample.get("title", ""),
        sample.get("content", ""),
        sample.get("metadata", {}),
    )
    logger.info("\n--- Sample embedding text (new format) ---")
    logger.info(sample_text)
    logger.info("------------------------------------------\n")

    if args.dry_run:
        logger.info("Dry run complete. Pass without --dry-run to reindex.")
        return

    # Re-initialize the vector store (clears and recreates collection)
    logger.info("Initializing embedder (INT8 ONNX Arctic)...")
    embedder = Embedder()

    logger.info(
        f"Clearing collection '{collection_name}' and re-embedding {len(documents)} documents..."
    )
    # Delete collection and recreate
    client.delete_collection(collection_name)
    logger.info("Old collection deleted.")

    vector_store = VectorStore(embedder=embedder, collection_name=collection_name)

    # Re-index in batches
    BATCH = 100
    total_success = 0
    total_fail = 0
    for i in range(0, len(documents), BATCH):
        batch = documents[i : i + BATCH]
        s, f = vector_store.add_documents_batch(batch)
        total_success += s
        total_fail += f
        logger.info(
            f"  Progress: {min(i + BATCH, len(documents))}/{len(documents)} (ok={total_success}, fail={total_fail})"
        )

    logger.info("=" * 60)
    logger.info(f"Re-indexing complete!")
    logger.info(f"  Success: {total_success}")
    logger.info(f"  Failed:  {total_fail}")
    stats = vector_store.get_collection_stats()
    logger.info(f"  Total in DB: {stats.get('total_documents', '?')}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
