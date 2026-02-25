#!/usr/bin/env python3
import json
import time
import requests

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

# Solo queries con complejidad semántica (sin títulos exactos)
queries_semantic = [
    "movies about artificial intelligence",
    "películas de robótica",
    "space exploration science fiction",
    "romantic comedy",
    "Christopher Nolan",
    "superhero action movie",
    "películas de ciencia ficción",
    "time travel paradox",
]

queries = queries_semantic

with open("baseline_minilm_results.json") as f:
    baseline = json.load(f)

baseline_times = {q["query"]: q["latency_ms"] for q in baseline["queries"]}
current_times = {}
headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

print("Ejecutando benchmark (queries con complejidad semántica)...\n")
for i, q in enumerate(queries, 1):
    try:
        start = time.time()
        r = requests.post(
            API_URL, json={"query": q, "top_k": 5}, headers=headers, timeout=30
        )
        latency = (time.time() - start) * 1000
        current_times[q] = latency
        print(f" {i:2}/8  ✓  {q[:35]:35}  {latency:7.1f}ms")
    except Exception as e:
        print(f" {i:2}/8  ✗  {q[:35]:35}  Error: {str(e)[:20]}")
        time.sleep(1)

print("\n" + "=" * 100)
print("COMPARATIVA: MiniLM-384D (Baseline) vs Arctic-768D ONNX (Actual)")
print("=" * 100)
print()

results = []
for q in queries:
    if q in baseline_times and q in current_times:
        b = baseline_times[q]
        c = current_times[q]
        diff = c - b
        pct = (diff / b) * 100
        results.append(
            {"query": q, "baseline": b, "current": c, "diff": diff, "pct": pct}
        )

# Print results
for r in results:
    bar_width = int(r["current"] / 100) if r["current"] < 2000 else 20
    bar = "█" * bar_width
    print(
        f"{r['query'][:35]:35}  {r['baseline']:7.0f}ms → {r['current']:7.0f}ms  {r['diff']:+7.0f}ms ({r['pct']:+6.1f}%)  {bar}"
    )

print()
print("=" * 100)
b_avg = sum(r["baseline"] for r in results) / len(results)
c_avg = sum(r["current"] for r in results) / len(results)
diff_avg = c_avg - b_avg
pct_avg = (diff_avg / b_avg) * 100
print(
    f"{'PROMEDIO':<35}  {b_avg:7.0f}ms → {c_avg:7.0f}ms  {diff_avg:+7.0f}ms ({pct_avg:+6.1f}%)"
)
print("=" * 100)
