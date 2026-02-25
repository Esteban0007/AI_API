#!/usr/bin/env python3
"""Test actual server-side latency"""
import sys

sys.path.insert(0, "/var/www/readyapi")

from app.engine.searcher import SearchEngine
import time

searcher = SearchEngine()

# Test cold start + warm cache
queries = [
    "movies about artificial intelligence",
    "películas de robótica",
    "space exploration science fiction",
]

for q in queries:
    start = time.time()
    results = searcher.search(q, top_k=10)
    elapsed = (time.time() - start) * 1000
    top_title = results[0].title if results else "NO RESULTS"
    print(f"{q[:40]:40} {elapsed:8.2f}ms -> {top_title[:40]}")
