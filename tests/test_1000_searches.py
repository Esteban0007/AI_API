#!/usr/bin/env python3
"""
Simple Load Test - 1000 Searches with "test" query
"""

import requests
import time
from statistics import mean, median

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_5DAsNmjt5iDxYLPVKzqF__rDSzpoBLA90P5-THRrX98"
NUM_SEARCHES = 1000

print("\n" + "=" * 70)
print(f"LOAD TEST - {NUM_SEARCHES} searches")
print("=" * 70 + "\n")

latencies = []
errors = 0
start_total = time.time()

for i in range(1, NUM_SEARCHES + 1):
    try:
        start = time.time()
        response = requests.post(
            API_URL,
            headers={"x-api-key": API_KEY},
            json={"query": "test", "top_k": 5, "include_content": True},
            timeout=30,
        )
        latency = (time.time() - start) * 1000
        latencies.append(latency)

        if response.status_code != 200:
            errors += 1

        if i % 100 == 0:
            print(
                f"  {i:4d}/{NUM_SEARCHES} | Avg: {mean(latencies):.1f}ms | Errors: {errors}"
            )

    except Exception as e:
        errors += 1
        if i % 100 == 0:
            print(f"  {i:4d}/{NUM_SEARCHES} | ERROR: {type(e).__name__}")

total_time = time.time() - start_total

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"Total: {NUM_SEARCHES} searches")
print(f"Time: {total_time:.2f}s")
print(f"Throughput: {NUM_SEARCHES / total_time:.2f} req/s")
print(f"Errors: {errors}/{NUM_SEARCHES} ({(errors/NUM_SEARCHES)*100:.1f}%)")
print(f"\nLatency:")
print(f"  Min: {min(latencies):.1f}ms")
print(f"  Max: {max(latencies):.1f}ms")
print(f"  Mean: {mean(latencies):.1f}ms")
print(f"  Median: {median(latencies):.1f}ms")

sorted_lat = sorted(latencies)
p95 = sorted_lat[int(len(latencies) * 0.95)]
p99 = sorted_lat[int(len(latencies) * 0.99)]
print(f"  P95: {p95:.1f}ms")
print(f"  P99: {p99:.1f}ms")

success = ((NUM_SEARCHES - errors) / NUM_SEARCHES) * 100
print(f"\nSuccess rate: {success:.1f}%")
print("=" * 70 + "\n")
