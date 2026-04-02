#!/usr/bin/env python3
"""
Benchmark test suite for ReadyAPI semantic search on MOVIES dataset
Measures: P95 latency + nDCG@5 accuracy for film recommendations
Models: Arctic (current) vs BGE-M3 (proposed)
"""

import requests
import json
import time
from typing import List, Dict, Tuple
import statistics
import re

# Test queries with expected relevant documents (ranked by relevance)
MOVIE_BENCHMARK_QUERIES = [
    # ENGLISH QUERIES - ACTION/ADVENTURE (25)
    {
        "query": "action packed adventure with explosions and fight scenes",
        "expected_keywords": ["action", "adventure", "fight", "explosion"],
        "lang": "en",
        "genre": "action",
    },
    {
        "query": "superhero comic book movie with special effects",
        "expected_keywords": ["superhero", "action", "special effects"],
        "lang": "en",
        "genre": "superhero",
    },
    {
        "query": "spy thriller with secret agents and missions",
        "expected_keywords": ["spy", "thriller", "agent", "mission"],
        "lang": "en",
        "genre": "spy",
    },
    {
        "query": "science fiction space adventure futuristic world",
        "expected_keywords": ["sci-fi", "space", "future", "alien"],
        "lang": "en",
        "genre": "scifi",
    },
    {
        "query": "horror scary movie with monsters and suspense",
        "expected_keywords": ["horror", "scary", "monster", "suspense"],
        "lang": "en",
        "genre": "horror",
    },
    {
        "query": "fantasy adventure magic kingdom dragons",
        "expected_keywords": ["fantasy", "magic", "dragon", "kingdom"],
        "lang": "en",
        "genre": "fantasy",
    },
    {
        "query": "comedy funny laugh out loud hilarious",
        "expected_keywords": ["comedy", "funny", "laugh", "hilarious"],
        "lang": "en",
        "genre": "comedy",
    },
    {
        "query": "romance love story emotional relationships",
        "expected_keywords": ["romance", "love", "relationship", "emotion"],
        "lang": "en",
        "genre": "romance",
    },
    {
        "query": "drama deep story character development intense",
        "expected_keywords": ["drama", "character", "intense", "emotional"],
        "lang": "en",
        "genre": "drama",
    },
    {
        "query": "thriller suspense mystery puzzle to solve",
        "expected_keywords": ["thriller", "mystery", "suspense", "puzzle"],
        "lang": "en",
        "genre": "thriller",
    },
    {
        "query": "animated cartoon animation families kids",
        "expected_keywords": ["animated", "cartoon", "animation", "family"],
        "lang": "en",
        "genre": "animated",
    },
    {
        "query": "western cowboy old west gunfight",
        "expected_keywords": ["western", "cowboy", "outlaw", "gunfight"],
        "lang": "en",
        "genre": "western",
    },
    {
        "query": "heist crime robbery steal treasure",
        "expected_keywords": ["heist", "crime", "robbery", "steal"],
        "lang": "en",
        "genre": "crime",
    },
    {
        "query": "war military battle soldiers combat",
        "expected_keywords": ["war", "military", "battle", "soldier"],
        "lang": "en",
        "genre": "war",
    },
    {
        "query": "adventure exploration discovery exotic locations",
        "expected_keywords": ["adventure", "exploration", "exotic", "discover"],
        "lang": "en",
        "genre": "adventure",
    },
    {
        "query": "blockbuster box office hit most popular",
        "expected_keywords": ["blockbuster", "popular", "hit", "box office"],
        "lang": "en",
        "genre": "blockbuster",
    },
    {
        "query": "indie independent film artistic vision",
        "expected_keywords": ["indie", "independent", "artistic", "film"],
        "lang": "en",
        "genre": "indie",
    },
    {
        "query": "classic timeless masterpiece iconic film",
        "expected_keywords": ["classic", "timeless", "masterpiece", "iconic"],
        "lang": "en",
        "genre": "classic",
    },
    {
        "query": "recent new release 2024 2025 latest movies",
        "expected_keywords": ["recent", "new", "latest", "release"],
        "lang": "en",
        "genre": "recent",
    },
    {
        "query": "family friendly movie kids can watch",
        "expected_keywords": ["family", "friendly", "kids", "children"],
        "lang": "en",
        "genre": "family",
    },
    {
        "query": "biographical life story real person historical",
        "expected_keywords": ["biographical", "biography", "life", "historical"],
        "lang": "en",
        "genre": "biography",
    },
    {
        "query": "documentary non-fiction real world educational",
        "expected_keywords": ["documentary", "non-fiction", "real", "educational"],
        "lang": "en",
        "genre": "documentary",
    },
    {
        "query": "musical songs dance performance entertainment",
        "expected_keywords": ["musical", "song", "dance", "performance"],
        "lang": "en",
        "genre": "musical",
    },
    {
        "query": "superhero team ensemble cast multiple heroes",
        "expected_keywords": ["superhero", "team", "ensemble", "hero"],
        "lang": "en",
        "genre": "ensemble",
    },
    {
        "query": "detective mystery detective solve crime case",
        "expected_keywords": ["detective", "mystery", "crime", "solve"],
        "lang": "en",
        "genre": "detective",
    },
    # SPANISH QUERIES - ACTION/ADVENTURE (25)
    {
        "query": "película de acción explosiones peleas luchas",
        "expected_keywords": ["acción", "explosión", "pelea", "lucha"],
        "lang": "es",
        "genre": "action",
    },
    {
        "query": "película de superhéroes cómics poderes especiales",
        "expected_keywords": ["superhéroe", "cómics", "poderes", "acción"],
        "lang": "es",
        "genre": "superhero",
    },
    {
        "query": "película de espías agentes secretos misiones",
        "expected_keywords": ["espía", "agente", "secreto", "misión"],
        "lang": "es",
        "genre": "spy",
    },
    {
        "query": "ciencia ficción futuro aliens espacial futurista",
        "expected_keywords": ["ciencia ficción", "futuro", "alien", "espacial"],
        "lang": "es",
        "genre": "scifi",
    },
    {
        "query": "película de terror miedo monstruos suspenso",
        "expected_keywords": ["terror", "miedo", "monstruo", "suspenso"],
        "lang": "es",
        "genre": "horror",
    },
    {
        "query": "fantasía aventura magia reino dragones",
        "expected_keywords": ["fantasía", "magia", "reino", "dragón"],
        "lang": "es",
        "genre": "fantasy",
    },
    {
        "query": "película cómica divertida risas humor",
        "expected_keywords": ["cómico", "divertido", "risa", "humor"],
        "lang": "es",
        "genre": "comedy",
    },
    {
        "query": "película romántica amor historia de amor",
        "expected_keywords": ["romance", "amor", "relación", "enamorado"],
        "lang": "es",
        "genre": "romance",
    },
    {
        "query": "película dramática emocionante personajes profundos",
        "expected_keywords": ["drama", "emocionante", "personaje", "intenso"],
        "lang": "es",
        "genre": "drama",
    },
    {
        "query": "suspenso misterio resolver acertijo intriga",
        "expected_keywords": ["suspenso", "misterio", "resolver", "intriga"],
        "lang": "es",
        "genre": "thriller",
    },
    {
        "query": "película animada dibujos animados familia niños",
        "expected_keywords": ["animado", "dibujo", "familia", "niños"],
        "lang": "es",
        "genre": "animated",
    },
    {
        "query": "película del oeste vaqueros duelo frontera",
        "expected_keywords": ["oeste", "vaquero", "duelo", "frontera"],
        "lang": "es",
        "genre": "western",
    },
    {
        "query": "robo crimen heist atraco tesoro",
        "expected_keywords": ["robo", "crimen", "atraco", "tesoro"],
        "lang": "es",
        "genre": "crime",
    },
    {
        "query": "película de guerra batalla soldados combate",
        "expected_keywords": ["guerra", "batalla", "soldado", "combate"],
        "lang": "es",
        "genre": "war",
    },
    {
        "query": "aventura exploración descubrimiento lugares exóticos",
        "expected_keywords": ["aventura", "exploración", "descubrimiento", "exótico"],
        "lang": "es",
        "genre": "adventure",
    },
    {
        "query": "película taquillera éxito popular más vista",
        "expected_keywords": ["taquilla", "éxito", "popular", "vista"],
        "lang": "es",
        "genre": "blockbuster",
    },
    {
        "query": "película independiente indie artística visión",
        "expected_keywords": ["independiente", "indie", "artística", "visión"],
        "lang": "es",
        "genre": "indie",
    },
    {
        "query": "clásico atemporal obra maestra icónica",
        "expected_keywords": ["clásico", "atemporal", "obra maestra", "icónica"],
        "lang": "es",
        "genre": "classic",
    },
    {
        "query": "estreno reciente película nueva 2024 2025",
        "expected_keywords": ["estreno", "reciente", "nueva", "última"],
        "lang": "es",
        "genre": "recent",
    },
    {
        "query": "película familiar apta para niños entretenida",
        "expected_keywords": ["familia", "niños", "apta", "entretenida"],
        "lang": "es",
        "genre": "family",
    },
    {
        "query": "película biográfica vida real persona histórica",
        "expected_keywords": ["biografía", "vida real", "histórica", "persona"],
        "lang": "es",
        "genre": "biography",
    },
    {
        "query": "documental no ficción mundo real educativa",
        "expected_keywords": ["documental", "no ficción", "real", "educativo"],
        "lang": "es",
        "genre": "documentary",
    },
    {
        "query": "película musical canciones baile actuación",
        "expected_keywords": ["musical", "canción", "baile", "actuación"],
        "lang": "es",
        "genre": "musical",
    },
    {
        "query": "equipo superhéroes múltiples héroes conjunto",
        "expected_keywords": ["equipo", "superhéroes", "conjunto", "héroes"],
        "lang": "es",
        "genre": "ensemble",
    },
    {
        "query": "detective misterio investigador resolver crimen",
        "expected_keywords": ["detective", "misterio", "investigador", "crimen"],
        "lang": "es",
        "genre": "detective",
    },
]


def extract_movie_titles_from_response(html: str) -> List[str]:
    """Extract movie titles from HTML response"""
    titles = []
    # Try multiple patterns
    patterns = [
        r'<div class="movie-title">([^<]+)</div>',
        r"<h3>([^<]+)</h3>",
        r"<strong>([^<]+)</strong>",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html)
        if matches:
            titles = matches[:5]
            break

    return titles


def calculate_relevance_score(
    actual_titles: List[str], expected_keywords: List[str]
) -> float:
    """
    Calculate relevance score based on keyword matching
    For movies, we check if titles contain expected genre/type keywords
    """
    if not actual_titles or not expected_keywords:
        return 0.0

    total_matches = 0
    for title in actual_titles:
        title_lower = title.lower()
        for keyword in expected_keywords:
            if keyword.lower() in title_lower:
                total_matches += 1

    # nDCG-like scoring (penalize position)
    score = 0.0
    position = 1
    matches_found = 0

    for title in actual_titles:
        title_lower = title.lower()
        for keyword in expected_keywords:
            if keyword.lower() in title_lower:
                score += 1.0 / (position**0.5 if position > 1 else 1)
                matches_found += 1
        position += 1

    # Normalize to 0-1
    max_possible = len(actual_titles) * (
        len(expected_keywords) / max(len(actual_titles), len(expected_keywords))
    )
    if max_possible == 0:
        return 0.0

    return min(score / max_possible, 1.0)


def run_movie_benchmark(server_url: str = "https://api.readyapi.net") -> Dict:
    """Run benchmark against production server with movies dataset"""

    results = {
        "timestamp": time.time(),
        "server": server_url,
        "dataset": "movies",
        "queries_tested": len(MOVIE_BENCHMARK_QUERIES),
        "latencies": [],
        "relevance_scores": [],
        "query_results": [],
    }

    print(f"\n🚀 MOVIES BENCHMARK STARTING")
    print(f"Server: {server_url}")
    print(f"Dataset: movies (2000+ films)")
    print(f"Queries: {len(MOVIE_BENCHMARK_QUERIES)}")
    print("-" * 70)

    for i, test_case in enumerate(MOVIE_BENCHMARK_QUERIES, 1):
        query = test_case["query"]
        keywords = test_case["expected_keywords"]
        lang = test_case["lang"]
        genre = test_case["genre"]

        try:
            # Measure latency
            start_time = time.time()
            response = requests.post(
                f"{server_url}/search-partial",
                data={"query": query, "dataset": "movies", "include_content": "false"},
                timeout=10,
            )
            latency = (time.time() - start_time) * 1000  # ms

            if response.status_code == 200:
                # Extract titles from HTML response
                html = response.text
                actual_titles = extract_movie_titles_from_response(html)

                # Calculate relevance score
                relevance = calculate_relevance_score(actual_titles, keywords)

                results["latencies"].append(latency)
                results["relevance_scores"].append(relevance)
                results["query_results"].append(
                    {
                        "query": query,
                        "lang": lang,
                        "genre": genre,
                        "latency_ms": round(latency, 2),
                        "relevance": round(relevance, 3),
                        "expected_keywords": keywords,
                        "actual_top5": actual_titles,
                    }
                )

                status = "✅" if relevance > 0.6 else "⚠️" if relevance > 0.3 else "❌"
                print(
                    f"{i:2d}. {status} {lang.upper()} {genre:12s} | {query[:35]:35s} | {latency:6.1f}ms | {relevance:.3f}"
                )
            else:
                print(
                    f"{i:2d}. ❌ {lang.upper()} | {query[:35]:35s} | ERROR {response.status_code}"
                )

        except Exception as e:
            print(
                f"{i:2d}. ❌ {lang.upper()} | {query[:35]:35s} | EXCEPTION: {str(e)[:30]}"
            )

    return results


def calculate_metrics(results: Dict) -> Dict:
    """Calculate summary metrics"""

    if not results["latencies"]:
        return {}

    latencies = results["latencies"]
    relevance_scores = results["relevance_scores"]

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
        "relevance": {
            "min": min(relevance_scores),
            "max": max(relevance_scores),
            "mean": statistics.mean(relevance_scores),
            "median": statistics.median(relevance_scores),
        },
    }

    return metrics


def print_report(results: Dict, metrics: Dict):
    """Print benchmark report"""

    print("\n" + "=" * 70)
    print("📊 MOVIES BENCHMARK RESULTS")
    print("=" * 70)

    print("\n⏱️  LATENCY METRICS (milliseconds)")
    print("-" * 70)
    print(f"  Min:    {metrics['latency']['min_ms']:7.1f} ms")
    print(f"  Max:    {metrics['latency']['max_ms']:7.1f} ms")
    print(f"  Mean:   {metrics['latency']['mean_ms']:7.1f} ms")
    print(f"  Median: {metrics['latency']['median_ms']:7.1f} ms")
    print(
        f"  P95:    {metrics['latency']['p95_ms']:7.1f} ms {'✅ PASS' if metrics['latency']['p95_ms'] < 500 else '❌ FAIL'} (requirement: < 500ms)"
    )
    print(f"  P99:    {metrics['latency']['p99_ms']:7.1f} ms")

    print("\n🎯 RELEVANCE METRICS (keyword matching)")
    print("-" * 70)
    print(f"  Min:    {metrics['relevance']['min']:7.3f}")
    print(f"  Max:    {metrics['relevance']['max']:7.3f}")
    print(f"  Mean:   {metrics['relevance']['mean']:7.3f}")
    print(f"  Median: {metrics['relevance']['median']:7.3f}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run benchmark
    results = run_movie_benchmark()

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Print report
    print_report(results, metrics)

    # Save results to JSON
    with open("benchmark_results_movies_arctic.json", "w") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2)

    print(f"\n💾 Results saved to benchmark_results_movies_arctic.json")
