#!/usr/bin/env python3
"""
Evaluate search quality and latency on a dataset of movies.
Runs semantic, multilingual, exact, and almost-exact title tests.
Saves a JSON report and prints a readable summary.
"""

import argparse
import json
import os
import random
import shutil
import time
from pathlib import Path
from typing import Dict, List
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from engine.store import VectorStore
from engine.searcher import SearchEngine


DATASET_PATH = Path("data/movies_dataset.json")
DEFAULT_TARGET_SIZE = 2000

SEMANTIC_QUERIES = [
    "movies about the struggle of artificial intelligence",
    "existential crisis in space",
    "a lonely astronaut facing despair",
    "the ethics of creating conscious machines",
]

MULTILINGUAL_QUERIES = [
    "películas de robótica",
    "drama amoroso",
    "film d'animazione",
    "avventura spaziale",
]

EXACT_TITLE_QUERIES = [
    "A Woman Scorned",
]

ALMOST_EXACT_QUERIES = [
    "A Woman Scorne",
    "Woman Scorned",
]


def load_documents(target_size: int) -> List[Dict]:
    data = json.loads(DATASET_PATH.read_text())
    documents = data.get("documents", [])

    if len(documents) == 0:
        raise RuntimeError("Dataset vacío en data/movies_dataset.json")

    if len(documents) >= target_size:
        return documents[:target_size]

    # If dataset smaller, sample with replacement to reach target size
    random.seed(42)
    expanded = list(documents)
    while len(expanded) < target_size:
        doc = random.choice(documents)
        dup = dict(doc)
        dup["id"] = f"{doc['id']}-dup-{len(expanded)}"
        expanded.append(dup)

    return expanded


def ensure_clean_dir(path: Path):
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def add_documents(store: VectorStore, docs: List[Dict], batch_size: int = 100):
    success = 0
    failure = 0
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        ok, fail = store.add_documents_batch(batch)
        success += ok
        failure += fail
    return success, failure


def run_queries(engine: SearchEngine, queries: List[str], top_k: int = 5):
    results = []
    for q in queries:
        res, latency_ms = engine.search(q, top_k=top_k, include_content=False)
        results.append(
            {
                "query": q,
                "latency_ms": latency_ms,
                "top_results": [
                    {"title": r.get("title", ""), "score": r.get("score", 0.0)}
                    for r in res
                ],
            }
        )
    return results


def avg_latency(items: List[Dict]) -> float:
    if not items:
        return 0.0
    return sum(i["latency_ms"] for i in items) / len(items)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to JSON report")
    parser.add_argument("--persist-dir", required=True, help="Chroma persist dir")
    parser.add_argument("--collection", required=True, help="Chroma collection name")
    parser.add_argument("--target-size", type=int, default=DEFAULT_TARGET_SIZE)
    args = parser.parse_args()

    persist_dir = Path(args.persist_dir)
    ensure_clean_dir(persist_dir)

    docs = load_documents(args.target_size)

    store = VectorStore(persist_dir=str(persist_dir), collection_name=args.collection)
    engine = SearchEngine(vector_store=store)

    t0 = time.time()
    success, failure = add_documents(store, docs)
    index_ms = (time.time() - t0) * 1000

    semantic = run_queries(engine, SEMANTIC_QUERIES)
    multilingual = run_queries(engine, MULTILINGUAL_QUERIES)
    exact = run_queries(engine, EXACT_TITLE_QUERIES)
    almost = run_queries(engine, ALMOST_EXACT_QUERIES)

    report = {
        "dataset_size": len(docs),
        "index_time_ms": index_ms,
        "documents_added": success,
        "documents_failed": failure,
        "semantic": semantic,
        "multilingual": multilingual,
        "exact": exact,
        "almost_exact": almost,
        "avg_latency_ms": {
            "semantic": avg_latency(semantic),
            "multilingual": avg_latency(multilingual),
            "exact": avg_latency(exact),
            "almost_exact": avg_latency(almost),
        },
    }

    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2))

    print("=" * 80)
    print("EVALUATION REPORT")
    print("=" * 80)
    print(f"Dataset size: {report['dataset_size']}")
    print(f"Index time: {report['index_time_ms']:.0f} ms")
    print(
        f"Docs added: {report['documents_added']} | failed: {report['documents_failed']}"
    )
    print("-")
    print("Average latency (ms):")
    for k, v in report["avg_latency_ms"].items():
        print(f"  {k}: {v:.2f}")

    def print_block(title, items):
        print("\n" + title)
        print("-" * len(title))
        for item in items:
            print(f"Query: {item['query']}")
            for idx, r in enumerate(item["top_results"], start=1):
                print(f"  #{idx} {r['title']} | score={r['score']:.4f}")
            print("")

    print_block("Semantic Understanding", semantic)
    print_block("Multilingual Test", multilingual)
    print_block("Exact Title Match", exact)
    print_block("Almost Exact Title Match", almost)

    print(f"\nSaved report to: {args.output}")


if __name__ == "__main__":
    main()
