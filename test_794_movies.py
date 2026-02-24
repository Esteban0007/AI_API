#!/usr/bin/env python3
"""Test 794 movies TMDB dataset with posters and genres."""

import subprocess
import json

tests = [
    ("Fight Club", "Exact"),
    ("Godfather", "Partial"),
    ("epic action adventure", "Semantic"),
]

print("\n🎬 TEST - 794 PELÍCULAS TMDB CON POSTER + GÉNEROS")
print("=" * 80)

for query, typ in tests:
    result = subprocess.run(
        [
            "curl",
            "-s",
            "-X",
            "POST",
            "https://api.readyapi.net/api/v1/search/query",
            "-H",
            "Content-Type: application/json",
            "-H",
            "X-API-Key: rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg",
            "-d",
            json.dumps({"query": query, "top_k": 3}),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    try:
        data = json.loads(result.stdout)
        latency = data["execution_time_ms"]
        results = data["results"]

        print(f"\n[{typ:12}] Query: '{query}' ({latency:.0f}ms)")
        for i, r in enumerate(results[:3], 1):
            genres = r["metadata"].get("genres", [])
            poster = r["metadata"].get("poster_path", "")[:45]
            print(f"   {i}. {r['title'][:32]:32} | Score: {r['score']:.2f}")
            print(f"      Genres: {', '.join(genres[:3]) if genres else 'N/A'}")
            if poster:
                print(f"      Poster: {poster}...")
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")

print("\n" + "=" * 80)
print("✅ Test completado")
