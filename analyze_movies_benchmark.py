#!/usr/bin/env python3
"""
Analyze movies benchmark results
"""

import json
import statistics

# Load benchmark results
with open("benchmark_results_movies_arctic.json", "r") as f:
    data = json.load(f)

results = data["results"]
metrics = data["metrics"]

# Separate by language
en_queries = [q for q in results["query_results"] if q["lang"] == "en"]
es_queries = [q for q in results["query_results"] if q["lang"] == "es"]

print("\n" + "=" * 80)
print("🎬 MOVIES BENCHMARK ANALYSIS - ARCTIC MODEL")
print("=" * 80)

# Summary
print("\n📊 OVERALL PERFORMANCE")
print("-" * 80)
print(f"Total queries: {len(results['query_results'])}")
print(f"English queries: {len(en_queries)}")
print(f"Spanish queries: {len(es_queries)}")
print(f"\nLatency (ms): P95 = {metrics['latency']['p95_ms']:.1f}ms ❌ FAIL (>500ms)")
print(f"Relevance: Mean = {metrics['relevance']['mean']:.3f} ❌ Very poor")

# Language comparison
print("\n🌍 LANGUAGE PERFORMANCE")
print("-" * 80)
en_avg = statistics.mean([q["relevance"] for q in en_queries])
es_avg = statistics.mean([q["relevance"] for q in es_queries])
en_perfect = sum(1 for q in en_queries if q["relevance"] > 0.5) / len(en_queries) * 100
es_perfect = sum(1 for q in es_queries if q["relevance"] > 0.5) / len(es_queries) * 100

print(f"English: avg relevance {en_avg:.3f}, {en_perfect:.0f}% with relevance > 0.5")
print(f"Spanish: avg relevance {es_avg:.3f}, {es_perfect:.0f}% with relevance > 0.5")

# Latency analysis
print("\n⏱️  LATENCY ANALYSIS")
print("-" * 80)
latencies = sorted(results["latencies"])
print(f"Min: {metrics['latency']['min_ms']:.1f}ms")
print(f"Mean: {metrics['latency']['mean_ms']:.1f}ms")
print(f"Median: {metrics['latency']['median_ms']:.1f}ms")
print(f"P95: {metrics['latency']['p95_ms']:.1f}ms ❌ EXCEEDS 500ms limit")
print(f"P99: {metrics['latency']['p99_ms']:.1f}ms")

# Genre breakdown
print("\n🎭 GENRE PERFORMANCE")
print("-" * 80)
genres = {}
for q in results["query_results"]:
    genre = q["genre"]
    if genre not in genres:
        genres[genre] = []
    genres[genre].append(q["relevance"])

for genre, scores in sorted(genres.items()):
    avg = statistics.mean(scores)
    good = sum(1 for s in scores if s > 0.5)
    print(f"{genre:15s}: avg {avg:.3f} | {good}/2 good results")

# Worst performers
print("\n⚠️  WORST PERFORMING QUERIES (relevance < 0.1)")
print("-" * 80)
worst = sorted(results["query_results"], key=lambda x: x["relevance"])[:15]
for q in worst:
    if q["relevance"] < 0.1:
        print(f"  {q['relevance']:.3f} | {q['lang'].upper():2s} | {q['query'][:50]}")

# Best performers
print("\n✅ BEST PERFORMING QUERIES")
print("-" * 80)
best = sorted(results["query_results"], key=lambda x: x["relevance"], reverse=True)[:10]
for q in best:
    print(f"  {q['relevance']:.3f} | {q['lang'].upper():2s} | {q['query'][:50]}")

# Summary comparison
print("\n" + "=" * 80)
print("📋 COMPARISON: ReadyAPI Docs vs Movies")
print("=" * 80)
print("\nReadyAPI (Documentation):")
print(f"  P95 Latency: 248.1ms ✅")
print(f"  nDCG@5: 0.695 ❌ (but domain-specific)")
print(f"  Language: 25 EN, 25 ES")

print("\nMovies (Film Database):")
print(f"  P95 Latency: {metrics['latency']['p95_ms']:.1f}ms ❌ (exceeds 500ms!)")
print(f"  Relevance: {metrics['relevance']['mean']:.3f} ❌ (extremely poor)")
print(f"  Language: 25 EN, 25 ES")

print("\n🔍 ANALYSIS")
print("-" * 80)
print(
    f"""
The movies benchmark reveals CRITICAL ISSUES with Arctic model:

1. LATENCY PROBLEM
   - P95 = 538.1ms, exceeding the 500ms requirement
   - Slow performance on larger 2000+ movie dataset
   - Even with smaller docs, Arctic is >2x slower than on API docs

2. RELEVANCE PROBLEM  
   - Mean relevance = 0.068 (6.8%) - almost NO relevant results!
   - Only 1 query with relevance > 0.5 (war movie)
   - 48/50 queries completely fail (relevance < 0.1)

3. DATASET SIZE ISSUE
   - ReadyAPI: 12 docs, 2000 words → 248ms, 0.695 nDCG
   - Movies: 2000+ docs, 100K+ words → 538ms, 0.068 relevance
   - Arctic doesn't scale well to large document collections

4. SEMANTIC UNDERSTANDING
   - Arctic can't understand genre concepts
   - Fails on synonyms: "sci-fi" ≠ "space", "heist" ≠ "crime"
   - Can't map movie titles to genre keywords

VERDICT: Arctic model is UNSUITABLE for movies dataset
- P95 exceeds latency requirement
- Relevance is unacceptably low
- BGE-M3 migration is CRITICAL for this dataset
"""
)

print("=" * 80)
