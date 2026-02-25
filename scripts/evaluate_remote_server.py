#!/usr/bin/env python3
"""
Evaluate search quality and latency against the REMOTE server API.
Tests semantic, multilingual, exact, and almost-exact title queries.
"""

import argparse
import json
import requests
import time
from typing import Dict, List

API_URL = "https://api.readyapi.net/api/v1/search/query"

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
    "Avatar",
    "A Woman Scorned",
]

ALMOST_EXACT_QUERIES = [
    "Woman Scorned",
    "Shawshank Redemption",
]


def run_queries_remote(api_key: str, queries: List[str], top_k: int = 5) -> List[Dict]:
    """Run queries against remote API server."""
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    results = []

    for q in queries:
        payload = {"query": q, "top_k": top_k}
        try:
            t_start = time.time()
            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
            latency_ms = (time.time() - t_start) * 1000

            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "query": q,
                        "latency_ms": latency_ms,
                        "total_results": data.get("total_results", 0),
                        "top_results": [
                            {"title": r.get("title", ""), "score": r.get("score", 0.0)}
                            for r in data.get("results", [])[:top_k]
                        ],
                    }
                )
            else:
                results.append(
                    {
                        "query": q,
                        "latency_ms": latency_ms,
                        "error": f"HTTP {response.status_code}",
                    }
                )
        except Exception as e:
            results.append(
                {
                    "query": q,
                    "error": str(e),
                }
            )

    return results


def avg_latency(items: List[Dict]) -> float:
    """Calculate average latency, excluding errors."""
    valid = [i["latency_ms"] for i in items if "latency_ms" in i and "error" not in i]
    if not valid:
        return 0.0
    return sum(valid) / len(valid)


def main():
    parser = argparse.ArgumentParser(description="Evaluate remote server performance")
    parser.add_argument("--api-key", required=True, help="API key for authentication")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    print("=" * 80)
    print("REMOTE SERVER EVALUATION")
    print("=" * 80)
    print(f"API URL: {API_URL}\n")

    semantic = run_queries_remote(args.api_key, SEMANTIC_QUERIES)
    multilingual = run_queries_remote(args.api_key, MULTILINGUAL_QUERIES)
    exact = run_queries_remote(args.api_key, EXACT_TITLE_QUERIES)
    almost = run_queries_remote(args.api_key, ALMOST_EXACT_QUERIES)

    report = {
        "api_url": API_URL,
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

    with open(args.output, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Average latency (ms):")
    for k, v in report["avg_latency_ms"].items():
        print(f"  {k}: {v:.2f}")

    def print_block(title, items):
        print("\n" + title)
        print("-" * len(title))
        for item in items:
            if "error" in item:
                print(f"❌ {item['query']}: {item['error']}")
            else:
                print(f"Query: {item['query']} ({item['latency_ms']:.0f}ms)")
                for idx, r in enumerate(item["top_results"], start=1):
                    print(f"  #{idx} {r['title']} (score={r['score']:.4f})")

    print_block("SEMANTIC UNDERSTANDING", semantic)
    print_block("MULTILINGUAL TESTS", multilingual)
    print_block("EXACT TITLE MATCH", exact)
    print_block("ALMOST-EXACT TITLE MATCH", almost)

    print(f"\n✅ Report saved to: {args.output}\n")


if __name__ == "__main__":
    main()
