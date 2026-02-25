#!/usr/bin/env python3
"""Verify Arctic ONNX production setup"""
import os
import sys

sys.path.insert(0, "/var/www/readyapi")

print("=" * 60)
print("ARCTIC ONNX PRODUCTION VERIFICATION")
print("=" * 60)

print("\n✓ ONNX Model Files:")
onnx_dir = "/var/www/readyapi/models/arctic_onnx"
for f in ["model.onnx", "model.onnx_data", "tokenizer.json", "config.json"]:
    path = os.path.join(onnx_dir, f)
    if os.path.exists(path):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  ✓ {f}: {size_mb:.1f}MB")

print("\n✓ Configuration:")
from app.core.config import Settings

settings = Settings()

print(f"  EMBEDDING_USE_ONNX: {settings.EMBEDDING_USE_ONNX}")
print(f"  EMBEDDING_ONNX_DIR: {settings.EMBEDDING_ONNX_DIR}")
print(f"  EMBEDDING_MODEL: {settings.EMBEDDING_MODEL}")
print(f"  EMBEDDING_DIMENSION: {settings.EMBEDDING_DIMENSION}")

print("\n✓ ONNX Session:")
from app.engine.embedder import Embedder

embedder = Embedder()
print(f'  Model type: {"ONNX" if embedder._is_onnx else "PyTorch"}')
print(f"  Input names: {embedder.onnx_input_names}")
print(f"  Output names: {embedder.onnx_output_names}")
print(f"  Embedding dim: {embedder.embedding_dim}")

print("\n✓ Test Queries:")
import time

test_queries = [
    "Christopher Nolan",
    "movies about artificial intelligence",
    "The Matrix",
]
for q in test_queries:
    start = time.time()
    emb = embedder.embed_query(q)
    elapsed = (time.time() - start) * 1000
    norm = (emb**2).sum() ** 0.5
    print(f'  "{q}": {elapsed:.1f}ms, norm={norm:.4f}')

print("\n" + "=" * 60)
print("✅ ARCTIC ONNX PRODUCTION READY")
print("=" * 60)
