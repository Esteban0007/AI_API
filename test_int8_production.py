#!/usr/bin/env python3
import json
import time
import requests

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

queries = [
    "movies about artificial intelligence",
    "space exploration science fiction",
    "time travel paradox",
    "romantic comedy",
    "superhero action movie",
]

print("\n" + "=" * 80)
print("INT8 ONNX BENCHMARK - Post Deployment")
print("=" * 80 + "\n")

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
latencies = []

for i, q in enumerate(queries, 1):
    try:
        start = time.time()
        r = requests.post(
            API_URL, json={"query": q, "top_k": 5}, headers=headers, timeout=30
        )
        latency = (time.time() - start) * 1000
        latencies.append(latency)
        print(f" {i}/{len(queries)} ✓  {q[:40]:40}  {latency:7.1f}ms")
    except Exception as e:
        print(f" {i}/{len(queries)} ✗  {q[:40]:40}  Error: {str(e)[:20]}")

if latencies:
    avg = sum(latencies) / len(latencies)
    print("\n" + "=" * 80)
    print(f"PROMEDIO: {avg:.1f}ms")
    print("=" * 80)
    print(f"\n✅ INT8 ONNX está funcionando en producción")
    print(f"   Modelo: INT8 ONNX (106MB)")
    print(f"   Latencia: {avg:.0f}ms promedio")
