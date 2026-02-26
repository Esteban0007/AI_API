#!/usr/bin/env python3
"""
Script de debug interactivo para probar el API
"""

import requests
import json
import sys

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"


def test_api(query: str, top_k: int = 5):
    """
    Test the API with a specific query and top_k
    """
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

    print(f"\n{'='*80}")
    print(f"API Test: query='{query}', top_k={top_k}")
    print(f"{'='*80}\n")

    try:
        response = requests.post(
            API_URL, json={"query": query, "top_k": top_k}, headers=headers, timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return

        data = response.json()

        # Show summary
        print(f"📊 SUMMARY:")
        print(f"   Query: '{data.get('query')}'")
        print(f"   Total results reported: {data.get('total_results')}")
        print(f"   Results array length: {len(data.get('results', []))}")
        print(f"   Execution time: {data.get('execution_time_ms'):.2f}ms")

        # Check if correct
        actual = len(data.get("results", []))
        if actual == top_k:
            print(f"\n✅ CORRECT: Requested {top_k}, received {actual}")
        elif actual < top_k:
            print(f"\n⚠️ FEWER RESULTS: Requested {top_k}, received {actual}")
            print(
                f"   (Possible reason: Database has fewer than {top_k} matching documents)"
            )
        else:
            print(f"\n❌ TOO MANY RESULTS: Requested {top_k}, received {actual}")
            print(f"   (Bug: API is returning more than requested)")

        # Show results
        print(f"\n📋 RESULTS ({actual}/{top_k}):")
        for i, result in enumerate(data.get("results", []), 1):
            print(f"\n   {i}. {result.get('title')} (ID: {result.get('id')})")
            print(f"      Score: {result.get('score'):.4f}")
            print(f"      Genres: {result.get('metadata', {}).get('genres', 'N/A')}")

        return data

    except requests.exceptions.Timeout:
        print(f"❌ Request timeout (>30s)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    # Test with user input or default
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:-1]) if len(sys.argv) > 2 else sys.argv[1]
        top_k = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 5
        test_api(query, top_k)
    else:
        # Interactive mode
        print("\nAPI Debug Tool - Test your queries\n")
        print("Usage: python3 this_script.py 'your query' [top_k]")
        print("Example: python3 this_script.py 'science fiction' 5\n")

        while True:
            query = input("Enter query (or 'exit' to quit): ").strip()
            if query.lower() == "exit":
                break

            top_k_str = input("Enter top_k (default 5): ").strip()
            top_k = int(top_k_str) if top_k_str.isdigit() else 5

            test_api(query, top_k)
