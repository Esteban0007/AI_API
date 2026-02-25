#!/usr/bin/env python3
"""
Comprehensive testing suite for Arctic ONNX implementation
Tests various query types, latencies, and quality metrics
"""
import requests
import json
import time
from datetime import datetime
from typing import List, Dict
import statistics

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

# Comprehensive test queries
EXTENDED_TESTS = [
    # Exact matches
    {"query": "Avatar", "type": "exact", "expected_top": "Avatar", "min_score": 0.99},
    {
        "query": "The Matrix",
        "type": "exact",
        "expected_top": "The Matrix",
        "min_score": 0.99,
    },
    {
        "query": "Inception",
        "type": "exact",
        "expected_top": "Inception",
        "min_score": 0.99,
    },
    # Director searches
    {
        "query": "Christopher Nolan",
        "type": "director",
        "expected_keywords": ["Interstellar", "Nolan"],
        "min_score": 0.4,
    },
    {
        "query": "Spielberg films",
        "type": "director",
        "expected_keywords": ["Spielberg", "Jurassic"],
        "min_score": 0.3,
    },
    # Genre searches
    {
        "query": "science fiction movies",
        "type": "genre",
        "expected_keywords": ["Sci-Fi", "Space"],
        "min_score": 0.3,
    },
    {
        "query": "action adventure",
        "type": "genre",
        "expected_keywords": ["Action", "Adventure"],
        "min_score": 0.3,
    },
    # Semantic searches
    {
        "query": "movies about time travel",
        "type": "semantic",
        "expected_keywords": ["time", "travel"],
        "min_score": 0.3,
    },
    {
        "query": "artificial intelligence and robots",
        "type": "semantic",
        "expected_keywords": ["AI", "robot"],
        "min_score": 0.2,
    },
    {
        "query": "space exploration",
        "type": "semantic",
        "expected_keywords": ["space", "planet"],
        "min_score": 0.3,
    },
    # Multilingual
    {
        "query": "películas de ciencia ficción",
        "type": "multilingual",
        "expected_keywords": ["space", "sci-fi"],
        "min_score": 0.2,
    },
    {
        "query": "películas de acción",
        "type": "multilingual",
        "expected_keywords": ["action"],
        "min_score": 0.2,
    },
    # Actor searches
    {
        "query": "Tom Hanks movies",
        "type": "actor",
        "expected_keywords": ["Hanks"],
        "min_score": 0.2,
    },
    # Emotion/theme searches
    {
        "query": "scary horror films",
        "type": "theme",
        "expected_keywords": ["horror", "scary"],
        "min_score": 0.2,
    },
    {
        "query": "romantic drama",
        "type": "theme",
        "expected_keywords": ["romance", "drama"],
        "min_score": 0.2,
    },
]


def execute_query(query: str, top_k: int = 10) -> Dict:
    """Execute a single search query and measure performance"""
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {"query": query, "top_k": top_k}

    start_time = time.time()
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        latency = (time.time() - start_time) * 1000

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
                "error": f"HTTP {response.status_code}",
                "latency_ms": round(latency, 2),
            }
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        return {
            "success": False,
            "error": str(e),
            "latency_ms": round(latency, 2),
        }


def check_result_quality(test_case: Dict, result: Dict) -> Dict:
    """Check if search result matches expected criteria"""
    if not result["success"] or not result["results"]:
        return {"passed": False, "reason": "No results"}

    top_result = result["results"][0]
    score = top_result.get("score", 0)
    title = top_result.get("title", "").lower()
    content = top_result.get("content", "").lower()

    # Check if this is an exact match test
    if test_case["type"] == "exact":
        expected = test_case["expected_top"].lower()
        if expected in title:
            if score >= test_case["min_score"]:
                return {"passed": True, "reason": "Exact match found"}
            else:
                return {"passed": False, "reason": f"Score too low: {score}"}
        else:
            return {"passed": False, "reason": f"Expected {expected}, got {title}"}

    # For other tests, check keywords
    if "expected_keywords" in test_case:
        keywords_found = sum(
            1
            for kw in test_case["expected_keywords"]
            if kw.lower() in title or kw.lower() in content
        )
        if keywords_found > 0:
            if score >= test_case["min_score"]:
                return {"passed": True, "reason": f"Found {keywords_found} keywords"}
            else:
                return {"passed": False, "reason": f"Score too low: {score}"}
        else:
            return {"passed": False, "reason": "No keywords found in results"}

    if score >= test_case["min_score"]:
        return {"passed": True, "reason": f"Score: {score}"}
    else:
        return {"passed": False, "reason": f"Score too low: {score}"}


def run_comprehensive_tests() -> Dict:
    """Run all comprehensive tests"""
    print("\n" + "=" * 80)
    print("ARCTIC ONNX COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Total tests: {len(EXTENDED_TESTS)}\n")

    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(EXTENDED_TESTS),
        "tests": [],
        "summary": {},
    }

    latencies = []
    passed_tests = 0
    failed_tests = 0

    for i, test_case in enumerate(EXTENDED_TESTS, 1):
        query = test_case["query"]
        test_type = test_case["type"]

        print(
            f"[{i:2d}/{len(EXTENDED_TESTS)}] {test_type:12} | {query[:40]:40}",
            end=" | ",
        )

        # Execute query
        query_result = execute_query(query, top_k=10)
        latencies.append(query_result["latency_ms"])

        # Check quality
        quality_check = check_result_quality(test_case, query_result)

        # Format output
        latency = query_result["latency_ms"]
        results_count = query_result.get("total_results", 0)
        top_title = (
            query_result["results"][0]["title"][:25]
            if query_result.get("results")
            else "NO RESULTS"
        )

        status_symbol = "✓" if quality_check["passed"] else "✗"
        print(
            f"{status_symbol} {latency:7.0f}ms | {results_count:2} results | {top_title:25}"
        )

        if quality_check["passed"]:
            passed_tests += 1
        else:
            failed_tests += 1
            print(f"           Reason: {quality_check['reason']}")

        results["tests"].append(
            {
                "query": query,
                "type": test_type,
                "latency_ms": latency,
                "total_results": results_count,
                "top_result": top_title,
                "passed": quality_check["passed"],
                "reason": quality_check["reason"],
            }
        )

    # Calculate statistics
    results["summary"] = {
        "total_tests": len(EXTENDED_TESTS),
        "passed": passed_tests,
        "failed": failed_tests,
        "pass_rate": round(passed_tests / len(EXTENDED_TESTS) * 100, 1),
        "latency": {
            "average_ms": round(statistics.mean(latencies), 2),
            "min_ms": round(min(latencies), 2),
            "max_ms": round(max(latencies), 2),
            "median_ms": round(statistics.median(latencies), 2),
            "stdev_ms": (
                round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0
            ),
        },
    }

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed:        {passed_tests}/{len(EXTENDED_TESTS)}")
    print(f"Failed:        {failed_tests}/{len(EXTENDED_TESTS)}")
    print(f"Pass Rate:     {results['summary']['pass_rate']}%")
    print(f"\nLatency Statistics:")
    print(f"  Average:   {results['summary']['latency']['average_ms']:.2f}ms")
    print(f"  Min:       {results['summary']['latency']['min_ms']:.2f}ms")
    print(f"  Max:       {results['summary']['latency']['max_ms']:.2f}ms")
    print(f"  Median:    {results['summary']['latency']['median_ms']:.2f}ms")
    print(f"  StdDev:    {results['summary']['latency']['stdev_ms']:.2f}ms")

    # Performance classification
    avg_latency = results["summary"]["latency"]["average_ms"]
    if avg_latency < 1000:
        perf_class = "🚀 EXCELLENT (< 1s)"
    elif avg_latency < 2000:
        perf_class = "✅ GOOD (1-2s)"
    elif avg_latency < 3000:
        perf_class = "⚠️  ACCEPTABLE (2-3s)"
    else:
        perf_class = "⚠️  SLOW (> 3s)"

    print(f"\nPerformance: {perf_class}")

    print("\n" + "=" * 80)

    return results


if __name__ == "__main__":
    results = run_comprehensive_tests()

    # Save results
    output_file = "comprehensive_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}\n")
