#!/usr/bin/env python3
"""Load TMDB dataset locally."""

import sys

sys.path.insert(0, "/Users/estebanbardolet/Desktop/API_IA")

from app.engine.store import VectorStore
from app.engine.embedder import Embedder
import json

print("Initializing vector store...")
embedder = Embedder()
vector_store = VectorStore(embedder=embedder, tenant_id="admin")

# Load TMDB dataset
with open("/Users/estebanbardolet/Desktop/API_IA/data/tmdb_movies.json") as f:
    data = json.load(f)

documents = data["documents"]
print(f"Loaded {len(documents)} documents from TMDB")

# Clear existing
print("Clearing existing collection...")
vector_store.clear_collection()

# Index
print("Indexing documents...")
success, fail = vector_store.add_documents_batch(documents)

print(f"\n✅ Successfully indexed: {success} documents")
if fail > 0:
    print(f"❌ Failed: {fail}")

# Verify
stats = vector_store.get_collection_stats()
print(f"\n📊 Collection stats:")
print(f"  Total: {stats.get('document_count', 0)}")
print(f"  Dimension: {stats.get('embedding_dimension', 0)}")
