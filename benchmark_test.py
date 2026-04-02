#!/usr/bin/env python3
"""
Benchmark test suite for ReadyAPI semantic search
Measures: P95 latency + nDCG@5 accuracy
Models: Arctic (current) vs BGE-M3 (proposed)
"""

import requests
import json
import time
from typing import List, Dict, Tuple
import statistics

# Test queries with expected relevant documents (ranked by relevance)
BENCHMARK_QUERIES = [
    # ENGLISH QUERIES (25)
    {
        "query": "How to sign up and get API key",
        "expected_order": [
            "How to Sign Up and Get Your API Key",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "uploading documents to search",
        "expected_order": [
            "How to Upload Your Documents to Search",
            "Understanding the JSON Format for Uploads",
        ],
        "lang": "en",
    },
    {
        "query": "JSON format structure fields",
        "expected_order": [
            "Understanding the JSON Format for Uploads",
            "How to Upload Your Documents to Search",
        ],
        "lang": "en",
    },
    {
        "query": "check statistics verify documents",
        "expected_order": [
            "Finding Your Documents After Upload - Check Statistics",
            "How to Upload Your Documents to Search",
        ],
        "lang": "en",
    },
    {
        "query": "common questions FAQ search",
        "expected_order": [
            "Making Search Work - Common Questions",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "Python JavaScript code example",
        "expected_order": [
            "Using Python or JavaScript Instead of Curl",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "API key security protection",
        "expected_order": [
            "Understanding Your API Key and Keeping It Safe",
            "How to Sign Up and Get Your API Key",
        ],
        "lang": "en",
    },
    {
        "query": "pricing plans early adopter free",
        "expected_order": ["Pricing Plans and Understanding Your Quota"],
        "lang": "en",
    },
    {
        "query": "testing demo interactive search",
        "expected_order": [
            "Testing Search with the Live Demo",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "troubleshooting help problems errors",
        "expected_order": [
            "Getting Help - What To Do When Something Goes Wrong",
            "Making Search Work - Common Questions",
        ],
        "lang": "en",
    },
    {
        "query": "semantic search meaning concept",
        "expected_order": [
            "Understanding What ReadyAPI Does",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "curl command request syntax",
        "expected_order": [
            "Making Your First Search Request",
            "How to Upload Your Documents to Search",
        ],
        "lang": "en",
    },
    {
        "query": "document upload batch API",
        "expected_order": [
            "How to Upload Your Documents to Search",
            "Understanding the JSON Format for Uploads",
        ],
        "lang": "en",
    },
    {
        "query": "response time latency performance",
        "expected_order": [
            "Making Search Work - Common Questions",
            "Testing Search with the Live Demo",
        ],
        "lang": "en",
    },
    {
        "query": "delete remove document API",
        "expected_order": [
            "Making Search Work - Common Questions",
            "Getting Help - What To Do When Something Goes Wrong",
        ],
        "lang": "en",
    },
    {
        "query": "top_k parameter results limit",
        "expected_order": [
            "Making Search Work - Common Questions",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "relevance score ranking results",
        "expected_order": [
            "Making Search Work - Common Questions",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "environment variables secrets management",
        "expected_order": [
            "Understanding Your API Key and Keeping It Safe",
            "Using Python or JavaScript Instead of Curl",
        ],
        "lang": "en",
    },
    {
        "query": "private documents account security",
        "expected_order": [
            "Making Search Work - Common Questions",
            "Understanding Your API Key and Keeping It Safe",
        ],
        "lang": "en",
    },
    {
        "query": "first search request example walkthrough",
        "expected_order": [
            "Making Your First Search Request",
            "How to Upload Your Documents to Search",
        ],
        "lang": "en",
    },
    {
        "query": "what is ReadyAPI does",
        "expected_order": [
            "Understanding What ReadyAPI Does",
            "Making Your First Search Request",
        ],
        "lang": "en",
    },
    {
        "query": "registration email verification account",
        "expected_order": ["How to Sign Up and Get Your API Key"],
        "lang": "en",
    },
    {
        "query": "quota limits searches per month",
        "expected_order": [
            "Pricing Plans and Understanding Your Quota",
            "Making Search Work - Common Questions",
        ],
        "lang": "en",
    },
    {
        "query": "invalid API key error solution",
        "expected_order": [
            "Getting Help - What To Do When Something Goes Wrong",
            "Understanding Your API Key and Keeping It Safe",
        ],
        "lang": "en",
    },
    {
        "query": "no results search troubleshooting fix",
        "expected_order": [
            "Getting Help - What To Do When Something Goes Wrong",
            "Making Search Work - Common Questions",
        ],
        "lang": "en",
    },
    # SPANISH QUERIES (25)
    {
        "query": "cómo registrarse y obtener clave API",
        "expected_order": ["How to Sign Up and Get Your API Key"],
        "lang": "es",
    },
    {
        "query": "subir documentos para buscar",
        "expected_order": [
            "How to Upload Your Documents to Search",
            "Understanding the JSON Format for Uploads",
        ],
        "lang": "es",
    },
    {
        "query": "formato JSON estructura campos",
        "expected_order": [
            "Understanding the JSON Format for Uploads",
            "How to Upload Your Documents to Search",
        ],
        "lang": "es",
    },
    {
        "query": "verificar documentos estadísticas",
        "expected_order": ["Finding Your Documents After Upload - Check Statistics"],
        "lang": "es",
    },
    {
        "query": "preguntas frecuentes búsqueda",
        "expected_order": ["Making Search Work - Common Questions"],
        "lang": "es",
    },
    {
        "query": "ejemplo código Python JavaScript",
        "expected_order": ["Using Python or JavaScript Instead of Curl"],
        "lang": "es",
    },
    {
        "query": "seguridad clave API proteger",
        "expected_order": ["Understanding Your API Key and Keeping It Safe"],
        "lang": "es",
    },
    {
        "query": "planes precio gratis early adopter",
        "expected_order": ["Pricing Plans and Understanding Your Quota"],
        "lang": "es",
    },
    {
        "query": "prueba demostración búsqueda interactiva",
        "expected_order": ["Testing Search with the Live Demo"],
        "lang": "es",
    },
    {
        "query": "ayuda problemas errores solución",
        "expected_order": ["Getting Help - What To Do When Something Goes Wrong"],
        "lang": "es",
    },
    {
        "query": "búsqueda semántica significado concepto",
        "expected_order": ["Understanding What ReadyAPI Does"],
        "lang": "es",
    },
    {
        "query": "comando curl sintaxis solicitud",
        "expected_order": ["Making Your First Search Request"],
        "lang": "es",
    },
    {
        "query": "subida lote documento API",
        "expected_order": ["How to Upload Your Documents to Search"],
        "lang": "es",
    },
    {
        "query": "tiempo respuesta latencia desempeño",
        "expected_order": ["Making Search Work - Common Questions"],
        "lang": "es",
    },
    {
        "query": "eliminar borrar documento",
        "expected_order": ["Making Search Work - Common Questions"],
        "lang": "es",
    },
    {
        "query": "parámetro top_k resultados límite",
        "expected_order": ["Making Search Work - Common Questions"],
        "lang": "es",
    },
    {
        "query": "puntuación relevancia ranking",
        "expected_order": ["Making Search Work - Common Questions"],
        "lang": "es",
    },
    {
        "query": "variables entorno secretos gestión",
        "expected_order": ["Understanding Your API Key and Keeping It Safe"],
        "lang": "es",
    },
    {
        "query": "documentos privados cuenta seguridad",
        "expected_order": ["Making Search Work - Common Questions"],
        "lang": "es",
    },
    {
        "query": "primera búsqueda ejemplo tutorial",
        "expected_order": ["Making Your First Search Request"],
        "lang": "es",
    },
    {
        "query": "qué es ReadyAPI funciona",
        "expected_order": ["Understanding What ReadyAPI Does"],
        "lang": "es",
    },
    {
        "query": "registro email verificación cuenta",
        "expected_order": ["How to Sign Up and Get Your API Key"],
        "lang": "es",
    },
    {
        "query": "límite cuota búsquedas mes",
        "expected_order": ["Pricing Plans and Understanding Your Quota"],
        "lang": "es",
    },
    {
        "query": "clave API inválida error solución",
        "expected_order": ["Getting Help - What To Do When Something Goes Wrong"],
        "lang": "es",
    },
    {
        "query": "sin resultados búsqueda solución",
        "expected_order": ["Getting Help - What To Do When Something Goes Wrong"],
        "lang": "es",
    },
]


def calculate_ndcg(
    actual_results: List[str], expected_order: List[str], k: int = 5
) -> float:
    """
    Calculate Normalized Discounted Cumulative Gain @ k
    Higher is better (max 1.0)
    """
    actual_top_k = actual_results[:k]

    # Calculate DCG
    dcg = 0.0
    for i, doc in enumerate(actual_top_k, 1):
        if doc in expected_order:
            # Relevance = 1 if in expected results, 0 otherwise
            relevance = 1.0 - (expected_order.index(doc) * 0.1)  # Penalize order
            dcg += relevance / (i**0.5 if i > 1 else 1)

    # Calculate ideal DCG (all expected results at top)
    ideal_dcg = 0.0
    for i in range(min(k, len(expected_order))):
        relevance = 1.0 - (i * 0.1)
        ideal_dcg += relevance / (i**0.5 if i > 1 else 1)

    # Normalized DCG
    if ideal_dcg == 0:
        return 0.0
    return dcg / ideal_dcg


def run_benchmark(server_url: str = "https://api.readyapi.net") -> Dict:
    """Run benchmark against production server"""

    results = {
        "timestamp": time.time(),
        "server": server_url,
        "queries_tested": len(BENCHMARK_QUERIES),
        "latencies": [],
        "ndcg_scores": [],
        "query_results": [],
    }

    print(f"\n🚀 BENCHMARK STARTING")
    print(f"Server: {server_url}")
    print(f"Queries: {len(BENCHMARK_QUERIES)}")
    print("-" * 70)

    for i, test_case in enumerate(BENCHMARK_QUERIES, 1):
        query = test_case["query"]
        expected = test_case["expected_order"]
        lang = test_case["lang"]

        try:
            # Measure latency
            start_time = time.time()
            response = requests.post(
                f"{server_url}/search-partial",
                data={"query": query, "dataset": "readyapi", "include_content": "true"},
                timeout=10,
            )
            latency = (time.time() - start_time) * 1000  # ms

            if response.status_code == 200:
                # Extract titles from HTML response (simplified)
                html = response.text
                # Find all movie-title divs
                actual_titles = []
                import re

                title_pattern = r'<div class="movie-title">([^<]+)</div>'
                matches = re.findall(title_pattern, html)
                actual_titles = matches[:5]  # Top 5

                # Calculate nDCG@5
                ndcg = calculate_ndcg(actual_titles, expected)

                results["latencies"].append(latency)
                results["ndcg_scores"].append(ndcg)
                results["query_results"].append(
                    {
                        "query": query,
                        "lang": lang,
                        "latency_ms": round(latency, 2),
                        "ndcg@5": round(ndcg, 3),
                        "expected": expected,
                        "actual_top5": actual_titles,
                    }
                )

                status = "✅" if ndcg > 0.7 else "⚠️"
                print(
                    f"{i:2d}. {status} {lang.upper()} | {query[:40]:40s} | {latency:6.1f}ms | nDCG: {ndcg:.3f}"
                )
            else:
                print(
                    f"{i:2d}. ❌ {lang.upper()} | {query[:40]:40s} | ERROR {response.status_code}"
                )

        except Exception as e:
            print(
                f"{i:2d}. ❌ {lang.upper()} | {query[:40]:40s} | EXCEPTION: {str(e)[:30]}"
            )

    return results


def calculate_metrics(results: Dict) -> Dict:
    """Calculate summary metrics"""

    if not results["latencies"]:
        return {}

    latencies = results["latencies"]
    ndcg_scores = results["ndcg_scores"]

    metrics = {
        "total_queries": len(latencies),
        "latency": {
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
            "p99_ms": (
                sorted(latencies)[int(len(latencies) * 0.99)]
                if len(latencies) > 1
                else latencies[0]
            ),
        },
        "accuracy": {
            "ndcg_min": min(ndcg_scores),
            "ndcg_max": max(ndcg_scores),
            "ndcg_mean": statistics.mean(ndcg_scores),
            "ndcg_median": statistics.median(ndcg_scores),
        },
        "requirements_met": {
            "p95_latency_lt_500ms": sorted(latencies)[int(len(latencies) * 0.95)] < 500,
            "ndcg_mean_gt_0_80": statistics.mean(ndcg_scores) > 0.80,
        },
    }

    return metrics


def print_report(results: Dict, metrics: Dict):
    """Print benchmark report"""

    print("\n" + "=" * 70)
    print("📊 BENCHMARK RESULTS")
    print("=" * 70)

    print("\n⏱️  LATENCY METRICS (milliseconds)")
    print("-" * 70)
    print(f"  Min:    {metrics['latency']['min_ms']:7.1f} ms")
    print(f"  Max:    {metrics['latency']['max_ms']:7.1f} ms")
    print(f"  Mean:   {metrics['latency']['mean_ms']:7.1f} ms")
    print(f"  Median: {metrics['latency']['median_ms']:7.1f} ms")
    print(
        f"  P95:    {metrics['latency']['p95_ms']:7.1f} ms {'✅ PASS' if metrics['requirements_met']['p95_latency_lt_500ms'] else '❌ FAIL'} (requirement: < 500ms)"
    )
    print(f"  P99:    {metrics['latency']['p99_ms']:7.1f} ms")

    print("\n🎯 ACCURACY METRICS (nDCG@5)")
    print("-" * 70)
    print(f"  Min:    {metrics['accuracy']['ndcg_min']:7.3f}")
    print(f"  Max:    {metrics['accuracy']['ndcg_max']:7.3f}")
    print(
        f"  Mean:   {metrics['accuracy']['ndcg_mean']:7.3f} {'✅ PASS' if metrics['requirements_met']['ndcg_mean_gt_0_80'] else '❌ FAIL'} (requirement: > 0.80)"
    )
    print(f"  Median: {metrics['accuracy']['ndcg_median']:7.3f}")

    print("\n✅ REQUIREMENTS CHECK")
    print("-" * 70)
    if metrics["requirements_met"]["p95_latency_lt_500ms"]:
        print(f"  ✅ P95 latency < 500ms: PASS ({metrics['latency']['p95_ms']:.1f}ms)")
    else:
        print(f"  ❌ P95 latency < 500ms: FAIL ({metrics['latency']['p95_ms']:.1f}ms)")

    if metrics["requirements_met"]["ndcg_mean_gt_0_80"]:
        print(f"  ✅ nDCG@5 > 0.80: PASS ({metrics['accuracy']['ndcg_mean']:.3f})")
    else:
        print(f"  ❌ nDCG@5 > 0.80: FAIL ({metrics['accuracy']['ndcg_mean']:.3f})")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run benchmark
    results = run_benchmark()

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Print report
    print_report(results, metrics)

    # Save results to JSON
    with open("benchmark_results_arctic.json", "w") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2)

    print(f"\n💾 Results saved to benchmark_results_arctic.json")
