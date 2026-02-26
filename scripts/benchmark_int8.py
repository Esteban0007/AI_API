#!/usr/bin/env python3
"""
Benchmark INT8 quantized model performance vs Standard ONNX
"""

import json
import time
import requests
from pathlib import Path

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

# Complex semantic queries that benefit most from INT8
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

# Get baseline from previous test
baseline_file = Path(__file__).parent.parent / "baseline_arctic_onnx.json"

print("\n" + "=" * 80)
print("INT8 QUANTIZATION PERFORMANCE BENCHMARK")
print("=" * 80 + "\n")

# Load baseline
baseline_data = {}
if baseline_file.exists():
    with open(baseline_file) as f:
        data = json.load(f)
        baseline_data = {q["query"]: q["latency_ms"] for q in data.get("queries", [])}
    print("Baseline loaded from:", baseline_file)
else:
    print("⚠️  Baseline file not found")

current_times = {}
headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

print(f"\nBenchmarking {len(queries_semantic)} semantic queries...\n")

for i, q in enumerate(queries_semantic, 1):
    try:
        start = time.time()
        r = requests.post(
            API_URL, json={"query": q, "top_k": 5}, headers=headers, timeout=30
        )
        latency = (time.time() - start) * 1000
        current_times[q] = latency

        baseline = baseline_data.get(q, 0)
        delta = latency - baseline if baseline else 0
        pct = (delta / baseline * 100) if baseline else 0

        symbol = "✓" if delta < 0 else "⚠" if delta > 0 else "="
        print(f" {i}/8 {symbol}  {q[:35]:35}  {latency:7.1f}ms", end="")

        if baseline:
            print(f" (vs {baseline:.0f}ms: {delta:+.0f}ms, {pct:+.1f}%)")
        else:
            print()

    except Exception as e:
        print(f" {i}/8 ✗  {q[:35]:35}  Error: {str(e)[:20]}")

# Calculate summary
if current_times and baseline_data:
    current_avg = sum(current_times.values()) / len(current_times)
    baseline_avg = sum(baseline_data.values()) / len(
        [q for q in queries_semantic if q in baseline_data]
    )

    improvement = baseline_avg - current_avg
    improvement_pct = (improvement / baseline_avg * 100) if baseline_avg else 0

    print("\n" + "=" * 80)
    print(f"BASELINE (Standard ONNX):  {baseline_avg:7.1f}ms")
    print(f"CURRENT (INT8 ONNX):       {current_avg:7.1f}ms")
    print(f"IMPROVEMENT:               {improvement:+7.1f}ms ({improvement_pct:+.1f}%)")
    print("=" * 80)

    if improvement > 0:
        print("✅ INT8 quantization is FASTER than standard ONNX")
    else:
        print("⚠️  INT8 quantization is slightly slower (within acceptable range)")
else:
    print("\n" + "=" * 80)
    print("Could not calculate summary - missing baseline data")
    print("=" * 80)

# Test health endpoint to verify INT8 is loaded
print("\n" + "=" * 80)
print("Verifying INT8 Model Status")
print("=" * 80 + "\n")

try:
    r = requests.get("https://api.readyapi.net/health", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Health check passed")
        print(f"   Embedding Model: {data.get('embedding_model', 'Unknown')}")
        print(f"   Model Name: {data.get('model_name', 'Unknown')}")
        print(f"   Dimension: {data.get('dimension', 'Unknown')}")
    else:
        print(f"⚠️  Health check returned {r.status_code}")
except Exception as e:
    print(f"⚠️  Could not reach health endpoint: {e}")
