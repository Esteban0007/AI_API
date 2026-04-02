#!/usr/bin/env python3
"""
Generate visual comparison charts for Arctic vs BGE-M3 benchmark
"""

import json
import statistics

# Load benchmark results
with open("benchmark_results_arctic.json", "r") as f:
    data = json.load(f)

results = data["results"]
metrics = data["metrics"]

# Separate by language
en_queries = [q for q in results["query_results"] if q["lang"] == "en"]
es_queries = [q for q in results["query_results"] if q["lang"] == "es"]

print("\n" + "=" * 80)
print("📊 BENCHMARK VISUALIZATION - ARCTIC MODEL")
print("=" * 80)

# Latency Distribution
print("\n⏱️  LATENCY DISTRIBUTION (milliseconds)")
print("-" * 80)
latencies = sorted(results["latencies"])
percentiles = [0, 25, 50, 75, 90, 95, 99, 100]
for p in percentiles:
    idx = int(len(latencies) * p / 100)
    if idx >= len(latencies):
        idx = len(latencies) - 1
    val = latencies[idx]
    bar = "█" * int(val / 50)
    print(f"  P{p:2d}: {val:6.1f}ms {bar}")

# nDCG Distribution
print("\n🎯 nDCG@5 DISTRIBUTION (accuracy)")
print("-" * 80)
ndcg_scores = sorted(results["ndcg_scores"])
for p in percentiles:
    idx = int(len(ndcg_scores) * p / 100)
    if idx >= len(ndcg_scores):
        idx = len(ndcg_scores) - 1
    val = ndcg_scores[idx]
    bar = "█" * int(val * 20)
    status = "✅" if val > 0.8 else "⚠️ " if val > 0.6 else "❌"
    print(f"  P{p:2d}: {val:.3f} {bar} {status}")

# Language comparison
print("\n🌍 LANGUAGE PERFORMANCE COMPARISON")
print("-" * 80)
en_avg = statistics.mean([q["ndcg@5"] for q in en_queries])
es_avg = statistics.mean([q["ndcg@5"] for q in es_queries])
en_pass = sum(1 for q in en_queries if q["ndcg@5"] > 0.7) / len(en_queries) * 100
es_pass = sum(1 for q in es_queries if q["ndcg@5"] > 0.7) / len(es_queries) * 100

print(f"English (25 queries)")
print(f"  Average nDCG@5: {en_avg:.3f} {'✅' if en_avg > 0.8 else '❌'}")
print(f"  Pass rate (>0.70): {en_pass:.0f}%")
print(
    f"  Average latency: {statistics.mean([q['latency_ms'] for q in en_queries]):.1f}ms"
)

print(f"\nSpanish (25 queries)")
print(f"  Average nDCG@5: {es_avg:.3f} {'✅' if es_avg > 0.8 else '❌'}")
print(f"  Pass rate (>0.70): {es_pass:.0f}%")
print(
    f"  Average latency: {statistics.mean([q['latency_ms'] for q in es_queries]):.1f}ms"
)

# Query performance histogram
print("\n📈 nDCG@5 HISTOGRAM")
print("-" * 80)
buckets = {
    "0.00-0.20": 0,
    "0.20-0.40": 0,
    "0.40-0.60": 0,
    "0.60-0.80": 0,
    "0.80-1.00": 0,
}

for score in results["ndcg_scores"]:
    if score < 0.2:
        buckets["0.00-0.20"] += 1
    elif score < 0.4:
        buckets["0.20-0.40"] += 1
    elif score < 0.6:
        buckets["0.40-0.60"] += 1
    elif score < 0.8:
        buckets["0.60-0.80"] += 1
    else:
        buckets["0.80-1.00"] += 1

for bucket, count in buckets.items():
    bar = "█" * count
    pct = count / len(results["ndcg_scores"]) * 100
    print(f"  {bucket}: {bar} {count:2d} queries ({pct:5.1f}%)")

# Worst performers
print("\n⚠️  WORST PERFORMING QUERIES (nDCG < 0.4)")
print("-" * 80)
worst = sorted(results["query_results"], key=lambda x: x["ndcg@5"])[:10]
for q in worst:
    if q["ndcg@5"] < 0.4:
        print(f"  {q['ndcg@5']:.3f} | {q['lang'].upper():2s} | {q['query'][:50]}")

# Best performers
print("\n✅ BEST PERFORMING QUERIES (nDCG = 1.0)")
print("-" * 80)
best = [q for q in results["query_results"] if q["ndcg@5"] == 1.0]
print(f"  {len(best)} perfect queries out of {len(results['query_results'])} total")
for q in best[:10]:
    print(f"  ✅ {q['lang'].upper():2s} | {q['query'][:50]}")

# Summary comparison table
print("\n" + "=" * 80)
print("📋 SUMMARY: ARCTIC vs BGE-M3 PROJECTION")
print("=" * 80)

arctic_metrics = {
    "Latency P95": f"{metrics['latency']['p95_ms']:.1f}ms",
    "Latency Mean": f"{metrics['latency']['mean_ms']:.1f}ms",
    "nDCG@5 Mean": f"{metrics['accuracy']['ndcg_mean']:.3f}",
    "English nDCG": f"{en_avg:.3f}",
    "Spanish nDCG": f"{es_avg:.3f}",
    "Model Size": "~400MB",
    "Memory Usage": "~2.5GB",
    "Passes Accuracy": "❌ NO",
}

bge_projection = {
    "Latency P95": "~250ms est.",
    "Latency Mean": "~235ms est.",
    "nDCG@5 Mean": "~0.85 est.",
    "English nDCG": "~0.82 est.",
    "Spanish nDCG": "~0.90 est.",
    "Model Size": "~680MB",
    "Memory Usage": "~2.8GB (INT8)",
    "Passes Accuracy": "✅ YES",
}

print("\n{:<25s} {:<20s} {:<20s}".format("Metric", "Arctic", "BGE-M3 (est.)"))
print("-" * 80)
for metric in arctic_metrics.keys():
    arctic_val = arctic_metrics[metric]
    bge_val = bge_projection[metric]
    print(f"{metric:<25s} {arctic_val:<20s} {bge_val:<20s}")

print("\n" + "=" * 80)
