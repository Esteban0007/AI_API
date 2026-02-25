#!/usr/bin/env python3
"""
Evaluation script for comparing embedding models
Runs standardized queries and measures performance
"""
import requests
import json
import time
from datetime import datetime
from typing import List, Dict

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

# Test queries covering different scenarios
TEST_QUERIES = [
    {
        "query": "Avatar",
        "type": "exact_match",
        "description": "Exact title match",
        "top_k": 5,
    },
    {
        "query": "movies about artificial intelligence",
        "type": "semantic",
        "description": "Semantic search - AI theme",
        "top_k": 10,
    },
    {
        "query": "películas de robótica",
        "type": "multilingual",
        "description": "Multilingual search - Spanish",
        "top_k": 10,
    },
    {
        "query": "space exploration science fiction",
        "type": "semantic",
        "description": "Semantic search - Space theme",
        "top_k": 10,
    },
    {
        "query": "romantic comedy",
        "type": "genre",
        "description": "Genre-based search",
        "top_k": 10,
    },
    {
        "query": "Christopher Nolan",
        "type": "director",
        "description": "Director search",
        "top_k": 10,
    },
    {
        "query": "superhero action movie",
        "type": "semantic",
        "description": "Semantic search - Superhero theme",
        "top_k": 10,
    },
    {
        "query": "The Matrix",
        "type": "exact_match",
        "description": "Exact title match - The Matrix",
        "top_k": 5,
    },
    {
        "query": "películas de ciencia ficción",
        "type": "multilingual",
        "description": "Multilingual search - Spanish SciFi",
        "top_k": 10,
    },
    {
        "query": "time travel paradox",
        "type": "semantic",
        "description": "Semantic search - Time travel theme",
        "top_k": 10,
    },
]


def execute_query(query: str, top_k: int = 10) -> Dict:
    """Execute a single search query and measure performance"""
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    payload = {"query": query, "top_k": top_k}

    start_time = time.time()
    response = requests.post(API_URL, json=payload, headers=headers)
    latency = (time.time() - start_time) * 1000  # Convert to ms

    if response.status_code == 200:
        data = response.json()
        return {
            "success": True,
            "latency_ms": round(latency, 2),
            "total_results": data.get("total_results", 0),
            "results": data.get("results", []),
        }
    else:
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}",
            "latency_ms": round(latency, 2),
        }


def run_evaluation(model_name: str) -> Dict:
    """Run all test queries and collect results"""
    print(f"\n{'='*60}")
    print(f"Starting evaluation for: {model_name}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    results = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "queries": [],
        "summary": {},
    }

    total_latency = 0
    successful_queries = 0

    for i, test_case in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] Testing: {test_case['description']}")
        print(f"  Query: \"{test_case['query']}\"")

        query_result = execute_query(test_case["query"], test_case["top_k"])

        if query_result["success"]:
            successful_queries += 1
            total_latency += query_result["latency_ms"]

            # Extract top 3 results for display
            top_results = [
                {
                    "title": r.get("title"),
                    "score": round(r.get("score", 0), 4),
                    "director": r.get("metadata", {}).get("director"),
                    "genres": r.get("metadata", {}).get("genres"),
                }
                for r in query_result["results"][:3]
            ]

            print(f"  ✓ Latency: {query_result['latency_ms']}ms")
            print(f"  ✓ Results: {query_result['total_results']}")
            if top_results:
                print(
                    f"  Top result: {top_results[0]['title']} (score: {top_results[0]['score']})"
                )

            results["queries"].append(
                {
                    "query": test_case["query"],
                    "type": test_case["type"],
                    "description": test_case["description"],
                    "top_k": test_case["top_k"],
                    "latency_ms": query_result["latency_ms"],
                    "total_results": query_result["total_results"],
                    "top_3_results": top_results,
                    "all_results": query_result["results"],
                }
            )
        else:
            print(f"  ✗ Failed: {query_result['error']}")
            results["queries"].append(
                {
                    "query": test_case["query"],
                    "type": test_case["type"],
                    "description": test_case["description"],
                    "error": query_result["error"],
                }
            )

        print()
        time.sleep(0.5)  # Small delay between queries

    # Calculate summary statistics
    if successful_queries > 0:
        avg_latency = total_latency / successful_queries
        results["summary"] = {
            "total_queries": len(TEST_QUERIES),
            "successful_queries": successful_queries,
            "failed_queries": len(TEST_QUERIES) - successful_queries,
            "average_latency_ms": round(avg_latency, 2),
            "min_latency_ms": round(
                min(q["latency_ms"] for q in results["queries"] if "latency_ms" in q), 2
            ),
            "max_latency_ms": round(
                max(q["latency_ms"] for q in results["queries"] if "latency_ms" in q), 2
            ),
        }

    return results


def save_results(results: Dict, filename: str):
    """Save evaluation results to JSON file"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n{'='*60}")
    print(f"Results saved to: {filename}")
    print(f"{'='*60}\n")


def print_summary(results: Dict):
    """Print evaluation summary"""
    summary = results.get("summary", {})
    print(f"\n{'='*60}")
    print(f"EVALUATION SUMMARY - {results['model_name']}")
    print(f"{'='*60}")
    print(f"Total queries:     {summary.get('total_queries', 0)}")
    print(f"Successful:        {summary.get('successful_queries', 0)}")
    print(f"Failed:            {summary.get('failed_queries', 0)}")
    print(f"Average latency:   {summary.get('average_latency_ms', 0)}ms")
    print(f"Min latency:       {summary.get('min_latency_ms', 0)}ms")
    print(f"Max latency:       {summary.get('max_latency_ms', 0)}ms")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys

    model_name = sys.argv[1] if len(sys.argv) > 1 else "MiniLM-384D"
    output_file = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"evaluation_{model_name.lower().replace('-', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    # Run evaluation
    results = run_evaluation(model_name)

    # Print summary
    print_summary(results)

    # Save results
    save_results(results, output_file)

    print(f"✓ Evaluation complete for {model_name}")
