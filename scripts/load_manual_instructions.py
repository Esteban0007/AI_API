#!/usr/bin/env python3
"""Load manual instructions dataset for definitions demo."""

import json
import sys
import logging
from app.engine.store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_manual_instructions():
    """Load manual instructions into user_7 tenant."""
    try:
        # Load JSON file
        with open("data/manual_instructions.json", "r") as f:
            data = json.load(f)

        documents = data.get("documents", [])
        logger.info(f"Loaded {len(documents)} documents from JSON")

        # Initialize vector store for user_7 (definitions dataset)
        vector_store = VectorStore(tenant_id="user_7")

        # Clear existing collection
        logger.info("Clearing existing collection...")
        vector_store.delete_collection()

        # Add documents
        logger.info(f"Adding {len(documents)} manual instructions...")
        for doc in documents:
            vector_store.add(
                doc_id=doc["id"],
                content=doc["content"],
                metadata={
                    "title": doc["title"],
                    "keywords": doc.get("keywords", []),
                    "source": "manual",
                },
            )

        logger.info(f"✅ Successfully loaded {len(documents)} manual instructions")

        # Verify
        stats = vector_store.get_stats()
        logger.info(f"Collection stats: {stats}")

    except Exception as e:
        logger.error(f"❌ Error loading manual instructions: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_manual_instructions()
