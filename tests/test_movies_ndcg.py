#!/usr/bin/env python3
"""
nDCG@5 Accuracy Test - Movies Demo
Tests semantic search ranking quality for movie recommendations
Target: nDCG@5 > 0.80
"""

import requests
import time
import math
from statistics import mean

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "what are you loking at? go get your own key :)"
COLLECTION = "movies_demo"  # Movies collection

# Movie queries with expected relevance
MOVIE_QUERIES = [
    {
        "query": "action movie with explosions and adventure",
        "expected_keywords": ["action", "adventure", "explosions", "fight"],
        "name": "Action/Adventure",
    },
    {
        "query": "romantic comedy love story",
        "expected_keywords": ["romance", "love", "comedy", "funny"],
        "name": "Romantic Comedy",
    },
    {
        "query": "science fiction space aliens",
        "expected_keywords": ["sci-fi", "space", "aliens", "future"],
        "name": "Sci-Fi/Space",
    },
    {
        "query": "horror thriller scary movie",
        "expected_keywords": ["horror", "scary", "thriller", "suspense"],
        "name": "Horror/Thriller",
    },
    {
        "query": "drama emotional family story",
        "expected_keywords": ["drama", "emotional", "family", "story"],
        "name": "Drama",
    },
    {
        "query": "fantasy magic creatures adventure",
        "expected_keywords": ["fantasy", "magic", "adventure", "creatures"],
        "name": "Fantasy",
    },
    {
        "query": "documentary true story real events",
        "expected_keywords": ["documentary", "real", "true", "events"],
        "name": "Documentary",
    },
]


class nDCGCalculator:
    """Calculate nDCG@5 metric"""

    @staticmethod
    def dcg_at_k(relevances, k=5):
        """DCG@k = sum(rel_i / log2(i+1))"""
        dcg = 0.0
        for i, rel in enumerate(relevances[:k], start=1):
            dcg += rel / math.log2(i + 1)
        return dcg

    @staticmethod
    def ndcg_at_k(relevances, k=5):
        """nDCG@k = DCG@k / IDCG@k"""
        dcg = nDCGCalculator.dcg_at_k(relevances, k)
        ideal_relevances = sorted(relevances, reverse=True)[:k]
        idcg = nDCGCalculator.dcg_at_k(ideal_relevances, k)
        return dcg / idcg if idcg > 0 else 0.0


def calculate_relevance(content, keywords):
    """Calculate relevance score based on keyword matches (0-1)"""
    if not content or not keywords:
        return 0.0

    content_lower = content.lower()
    matches = sum(1 for kw in keywords if kw.lower() in content_lower)
    return min(1.0, matches / len(keywords))


def run_movie_accuracy_test():
    """Run nDCG@5 accuracy test on movies demo"""

    print("\n" + "=" * 80)
    print("MOVIES DEMO - nDCG@5 ACCURACY TEST")
    print("=" * 80)
    print(f"API URL: {API_URL}")
    print(f"Collection: {COLLECTION}")
    print(f"Target: nDCG@5 > 0.80\n")

    all_ndcg_scores = []
    all_latencies = []

    calculator = nDCGCalculator()

    for idx, test_case in enumerate(MOVIE_QUERIES, 1):
        query = test_case["query"]
        keywords = test_case["expected_keywords"]
        name = test_case["name"]

        print(f"\n[{idx:02d}] {name}")
        print(f'    Query: "{query}"')
        print(f"    Expected keywords: {keywords}")

        try:
            # Execute search
            start_time = time.time()
            response = requests.post(
                API_URL,
                headers={"x-api-key": API_KEY},
                json={
                    "query": query,
                    "top_k": 5,
                    "include_content": True,
                    "collection_name": COLLECTION,
                },
                timeout=30,
            )
            latency = (time.time() - start_time) * 1000  # ms
            all_latencies.append(latency)

            if response.status_code != 200:
                print(f"    ❌ ERROR: HTTP {response.status_code}")
                continue

            try:
                data = response.json()
                results = data.get("results", [])

                if not results:
                    print(f"    ⚠️  No results returned")
                    continue

                # Calculate relevance for each result
                relevance_scores = []

                print(f"    Results (top 5):")
                for rank, result in enumerate(results[:5], 1):
                    title = result.get("title", "Unknown")
                    content = result.get("content", "")
                    score = result.get("score", 0)

                    # Calculate relevance based on keywords
                    relevance = calculate_relevance(title + " " + content, keywords)
                    relevance_scores.append(relevance)

                    relevance_indicator = (
                        "⭐" if relevance >= 0.8 else "✓" if relevance >= 0.5 else "○"
                    )
                    print(f"      {rank}. [{relevance_indicator}] {title[:50]}")
                    print(
                        f"         API Score: {score:.4f} | Relevance: {relevance:.2f}"
                    )

                # Calculate nDCG@5
                ndcg_5 = calculator.ndcg_at_k(relevance_scores, k=5)
                all_ndcg_scores.append(ndcg_5)

                # Status
                status = "✅ PASS" if ndcg_5 > 0.80 else "⚠️ BELOW"
                print(f"\n    nDCG@5: {ndcg_5:.4f} {status}")
                print(f"    Latency: {latency:.1f}ms")

            except Exception as e:
                print(f"    ❌ Parse error: {e}")

        except requests.exceptions.Timeout:
            print(f"    ❌ TIMEOUT (>30s)")
        except requests.exceptions.ConnectionError:
            print(f"    ❌ CONNECTION ERROR")
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)[:50]}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if all_ndcg_scores:
        avg_ndcg = mean(all_ndcg_scores)
        min_ndcg = min(all_ndcg_scores)
        max_ndcg = max(all_ndcg_scores)
        avg_latency = mean(all_latencies) if all_latencies else 0

        print(f"\nQueries Tested: {len(all_ndcg_scores)}")
        print(f"Average nDCG@5: {avg_ndcg:.4f}")
        print(f"Min nDCG@5: {min_ndcg:.4f}")
        print(f"Max nDCG@5: {max_ndcg:.4f}")
        print(f"Average Latency: {avg_latency:.1f}ms")

        print(f"\nIndividual Scores:")
        for i, (test_case, score) in enumerate(zip(MOVIE_QUERIES, all_ndcg_scores), 1):
            status = "✅" if score > 0.80 else "⚠️"
            print(f"  {i}. {test_case['name']:20} {score:.4f} {status}")

        # Final verdict
        print("\n" + "=" * 80)
        passed = all(score > 0.80 for score in all_ndcg_scores)

        if passed:
            print("✅ ALL TESTS PASSED - nDCG@5 > 0.80")
            print(f"   Average: {avg_ndcg:.4f} > 0.80")
            return True
        elif avg_ndcg > 0.80:
            print(
                "⚠️  PARTIAL PASS - Average nDCG@5 > 0.80 but some queries below threshold"
            )
            print(f"   Average: {avg_ndcg:.4f} (individual minimum: {min_ndcg:.4f})")
            return True
        else:
            print("❌ FAILED - nDCG@5 below target")
            print(f"   Average: {avg_ndcg:.4f} < 0.80")
            return False
    else:
        print("❌ No results to evaluate")
        return False


if __name__ == "__main__":
    import sys

    success = run_movie_accuracy_test()
    sys.exit(0 if success else 1)
