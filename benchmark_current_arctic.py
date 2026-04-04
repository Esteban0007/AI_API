#!/usr/bin/env python3
"""
Benchmark test for current Arctic model with 2 workers
Tests: P95 latency, nDCG@5 accuracy, English & Spanish
"""

import requests
import time
import json
from statistics import mean, median, quantiles
from collections import defaultdict

API_URL = "https://api.readyapi.net/api/v1/search/query"
ADMIN_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

# Test queries with expected top results (keywords to match)
QUERIES = [
    # English - ReadyAPI docs
    {
        "query": "API authentication",
        "lang": "en",
        "collection": "user_8",
        "expected": ["API", "key", "authentication", "security"],
    },
    {
        "query": "search endpoint",
        "lang": "en",
        "collection": "user_8",
        "expected": ["search", "query", "POST", "endpoint"],
    },
    {
        "query": "rate limiting",
        "lang": "en",
        "collection": "user_8",
        "expected": ["rate", "limit", "requests", "plan"],
    },
    {
        "query": "pricing plans",
        "lang": "en",
        "collection": "user_8",
        "expected": ["free", "pro", "enterprise", "pricing"],
    },
    {
        "query": "API documentation",
        "lang": "en",
        "collection": "user_8",
        "expected": ["documentation", "API", "endpoints", "reference"],
    },
    # Spanish - ReadyAPI docs
    {
        "query": "autenticación de API",
        "lang": "es",
        "collection": "user_8",
        "expected": ["autenticación", "API", "clave", "seguridad"],
    },
    {
        "query": "búsqueda endpoint",
        "lang": "es",
        "collection": "user_8",
        "expected": ["búsqueda", "consulta", "endpoint", "POST"],
    },
    {
        "query": "limitación de velocidad",
        "lang": "es",
        "collection": "user_8",
        "expected": ["límite", "solicitudes", "velocidad"],
    },
    {
        "query": "planes de precios",
        "lang": "es",
        "collection": "user_8",
        "expected": ["gratis", "pro", "empresa", "precio"],
    },
    {
        "query": "documentación de API",
        "lang": "es",
        "collection": "user_8",
        "expected": ["documentación", "API", "referencia"],
    },
]


def calculate_ndcg(results, expected_keywords):
    """Calculate nDCG@5 based on keyword matching"""
    if not results or not expected_keywords:
        return 0.0

    # Ideal DCG (all relevant results at top)
    idcg = sum(1.0 / (i + 1) for i in range(min(5, len(expected_keywords))))

    # Actual DCG
    dcg = 0.0
    for i, result in enumerate(results[:5]):
        content = (result.get("content", "") + " " + result.get("title", "")).lower()
        # Check how many keywords are in this result
        keyword_matches = sum(1 for kw in expected_keywords if kw.lower() in content)
        if keyword_matches > 0:
            dcg += keyword_matches / (i + 1)

    ndcg = dcg / idcg if idcg > 0 else 0.0
    return min(1.0, ndcg)  # Cap at 1.0


def run_benchmark():
    """Run benchmark tests"""
    results = {
        "english": {"latencies": [], "ndcgs": [], "passes": 0},
        "spanish": {"latencies": [], "ndcgs": [], "passes": 0},
        "combined": {"latencies": [], "ndcgs": [], "passes": 0},
    }

    print("=" * 70)
    print("ARCTIC BENCHMARK TEST - Current Server (2 Workers)")
    print("=" * 70)
    print()

    for idx, test in enumerate(QUERIES, 1):
        query = test["query"]
        lang = test["lang"]
        collection = test["collection"]
        expected = test["expected"]

        print(f"[{idx:02d}] {lang.upper():2} | {query[:40]:40} | ", end="", flush=True)

        try:
            start = time.time()
            response = requests.post(
                API_URL,
                headers={"x-api-key": ADMIN_KEY},
                json={
                    "query": query,
                    "top_k": 5,
                    "include_content": True,
                    "collection_name": collection,
                },
                timeout=10,
            )
            latency = (time.time() - start) * 1000  # ms

            if response.status_code != 200:
                print(f"ERROR {response.status_code}")
                continue

            try:
                data = response.json()
                results_list = data.get("results", [])
                if not results_list and "response" in data:
                    results_list = data.get("response", [])
            except:
                print(f"JSON ERROR")
                continue
            # Determine pass/fail
            latency_pass = "✅" if latency < 500 else "❌"
            ndcg_pass = "✅" if ndcg > 0.80 else "❌"

            print(f"{latency:6.1f}ms {latency_pass} | nDCG: {ndcg:.3f} {ndcg_pass}")


            # Track results
            results[lang]["latencies"].append(latency)
            results[lang]["ndcgs"].append(ndcg)
            results["combined"]["latencies"].append(latency)
            results["combined"]["ndcgs"].append(ndcg)

            if latency < 500:
                results[lang]["passes"] += 1
                results["combined"]["passes"] += 1

        except Exception as e:
            print(f"ERROR: {str(e)[:30]}")

    # Print summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for lang_key, label in [
        ("english", "🇬🇧 ENGLISH"),
        ("spanish", "🇪🇸 SPANISH"),
        ("combined", "📊 COMBINED"),
    ]:
        data = results[lang_key]
        if data["latencies"]:
            latencies = data["latencies"]
            ndcgs = data["ndcgs"]

            p95_latency = (
                quantiles(latencies, n=20)[18] if len(latencies) > 1 else latencies[0]
            )
            avg_latency = mean(latencies)
            avg_ndcg = mean(ndcgs)

            latency_status = "✅ PASS" if p95_latency < 500 else "❌ FAIL"
            ndcg_status = "✅ PASS" if avg_ndcg > 0.80 else "❌ FAIL"

            print(f"\n{label}")
            print(
                f"  P95 Latency: {p95_latency:6.1f}ms (target <500ms) {latency_status}"
            )
            print(f"  Avg Latency: {avg_latency:6.1f}ms")
            print(f"  nDCG@5 Avg: {avg_ndcg:6.3f} (target >0.80) {ndcg_status}")
            print(f"  Tests: {len(latencies)}")

    print()
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    combined_ndcg = mean(results["combined"]["ndcgs"])
    combined_p95 = (
        quantiles(results["combined"]["latencies"], n=20)[18]
        if len(results["combined"]["latencies"]) > 1
        else results["combined"]["latencies"][0]
    )

    if combined_p95 >= 500:
        print("❌ P95 Latency EXCEEDS target - Consider:")
        print("   - Reduce more workers (1 worker)")
        print("   - Increase server RAM/CPU")
        print("   - Migrate to lighter model (BGE-M3)")
    else:
        print("✅ P95 Latency is acceptable")

    if combined_ndcg < 0.80:
        print("❌ nDCG@5 BELOW target - Consider:")
        print("   - Migrate to BGE-M3 INT8 (much better accuracy)")
        print("   - Current Arctic: not suitable for production")
    else:
        print("✅ nDCG@5 meets accuracy target")

    print()


if __name__ == "__main__":
    run_benchmark()
