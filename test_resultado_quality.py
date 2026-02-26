#!/usr/bin/env python3
"""
Test de Calidad de Resultados - Verificar relevancia y ranking
"""

import requests
import json

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test cases con queries y resultados esperados
test_cases = [
    {
        "query": "Avatar",
        "top_k": 5,
        "expected_top_result": "Avatar",
        "description": "Búsqueda de título exacto",
    },
    {
        "query": "science fiction",
        "top_k": 5,
        "expected_genre": "Science Fiction",
        "description": "Películas de ciencia ficción",
    },
    {
        "query": "action adventure",
        "top_k": 5,
        "expected_genres": ["Action", "Adventure"],
        "description": "Películas de acción/aventura",
    },
    {
        "query": "superhero",
        "top_k": 5,
        "expected_keywords": ["superhero", "hero", "action"],
        "description": "Películas de superhéroes",
    },
    {
        "query": "time travel",
        "top_k": 5,
        "expected_keywords": ["time", "travel", "paradox", "temporal"],
        "description": "Películas de viajes en el tiempo",
    },
    {
        "query": "romantic comedy",
        "top_k": 5,
        "expected_genre": "Comedy",
        "description": "Películas románticas/comedia",
    },
]

print("\n" + "=" * 100)
print("TEST DE CALIDAD: Verificar Relevancia y Ranking de Resultados")
print("=" * 100 + "\n")

overall_stats = {
    "total_tests": 0,
    "relevant_results": 0,
    "accurate_rankings": 0,
    "correct_scores": 0,
}

for test in test_cases:
    print(f"TEST: {test['description']}")
    print(f"Query: '{test['query']}' (top_k={test['top_k']})")
    print("-" * 100)

    try:
        response = requests.post(
            API_URL,
            json={"query": test["query"], "top_k": test["top_k"]},
            headers=headers,
            timeout=30,
        )

        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}\n")
            continue

        data = response.json()
        results = data.get("results", [])

        # Verificación 1: Número de resultados
        if len(results) == test["top_k"]:
            print(
                f"✅ Cantidad: {len(results)} resultados (solicitados {test['top_k']})"
            )
        else:
            print(
                f"⚠️  Cantidad: {len(results)} resultados (solicitados {test['top_k']})"
            )

        # Verificación 2: Scores son decrecientes
        scores_decreasing = all(
            results[i]["score"] >= results[i + 1]["score"]
            for i in range(len(results) - 1)
        )
        if scores_decreasing:
            print(f"✅ Ranking: Scores decrecientes (correcto)")
        else:
            print(f"❌ Ranking: Scores NO son decrecientes (error)")

        # Mostrar resultados
        print(f"\n📋 RESULTADOS:\n")
        relevant_count = 0

        for i, result in enumerate(results, 1):
            title = result.get("title", "")
            score = result.get("score", 0)
            genres = result.get("metadata", {}).get("genres", [])

            # Evaluar relevancia
            is_relevant = False
            relevance_reason = ""

            # Check expected_top_result
            if "expected_top_result" in test:
                if i == 1 and test["expected_top_result"].lower() in title.lower():
                    is_relevant = True
                    relevance_reason = f"Top result es '{test['expected_top_result']}'"

            # Check expected_genre
            elif "expected_genre" in test:
                if test["expected_genre"] in genres:
                    is_relevant = True
                    relevance_reason = f"Tiene género '{test['expected_genre']}'"

            # Check expected_genres
            elif "expected_genres" in test:
                if any(g in genres for g in test["expected_genres"]):
                    is_relevant = True
                    relevance_reason = f"Tiene géneros relevantes {genres}"

            # Check keywords
            elif "expected_keywords" in test:
                title_lower = title.lower()
                if any(kw.lower() in title_lower for kw in test["expected_keywords"]):
                    is_relevant = True
                    relevance_reason = f"Título contiene palabras clave"

            if is_relevant:
                relevant_count += 1

            status = "✅" if is_relevant else "⚠️"
            print(f"   {i}. {title}")
            print(f"      Score: {score:.4f} | Géneros: {genres}")
            print(f"      {status} {relevance_reason}\n")

        # Estadísticas
        relevance_pct = (relevant_count / len(results)) * 100 if results else 0
        print(
            f"📊 RELEVANCIA: {relevant_count}/{len(results)} resultados relevantes ({relevance_pct:.0f}%)"
        )

        overall_stats["total_tests"] += 1
        if relevant_count == len(results):
            overall_stats["relevant_results"] += 1
        if scores_decreasing:
            overall_stats["accurate_rankings"] += 1

        print("\n" + "=" * 100 + "\n")

    except Exception as e:
        print(f"❌ Error: {str(e)}\n")

# Resumen final
print("=" * 100)
print("RESUMEN GENERAL")
print("=" * 100 + "\n")

if overall_stats["total_tests"] > 0:
    relevance_rate = (
        overall_stats["relevant_results"] / overall_stats["total_tests"]
    ) * 100
    ranking_rate = (
        overall_stats["accurate_rankings"] / overall_stats["total_tests"]
    ) * 100

    print(f"Tests ejecutados: {overall_stats['total_tests']}")
    print(
        f"Tests con todos relevantes: {overall_stats['relevant_results']} ({relevance_rate:.0f}%)"
    )
    print(
        f"Tests con ranking correcto: {overall_stats['accurate_rankings']} ({ranking_rate:.0f}%)"
    )

    print("\n📊 CONCLUSIÓN:\n")

    if relevance_rate >= 80:
        print(f"✅ CALIDAD BUENA: {relevance_rate:.0f}% de resultados son relevantes")
        print("   El API está devolviendo resultados de alta calidad")
    elif relevance_rate >= 60:
        print(f"⚠️  CALIDAD MEDIA: {relevance_rate:.0f}% de resultados son relevantes")
        print("   Podría mejorar la relevancia con mejor tuning del modelo")
    else:
        print(f"❌ CALIDAD BAJA: {relevance_rate:.0f}% de resultados son relevantes")
        print("   Se necesita mejorar el modelo o los embeddings")

    if ranking_rate == 100:
        print(f"✅ RANKING: Perfecto - todos los scores son decrecientes")
    else:
        print(f"⚠️  RANKING: {ranking_rate:.0f}% de tests tienen ranking correcto")

print("\n" + "=" * 100 + "\n")
