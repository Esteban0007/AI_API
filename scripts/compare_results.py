#!/usr/bin/env python3
"""
Compare results from MiniLM vs Arctic Embed evaluations
"""
import json
import sys


def load_results(filename):
    with open(filename, "r") as f:
        return json.load(f)


def compare_models(minilm_file, arctic_file):
    minilm = load_results(minilm_file)
    arctic = load_results(arctic_file)

    print("=" * 80)
    print("COMPARATIVA: MiniLM-384D vs Arctic-768D")
    print("=" * 80)

    # Performance comparison
    print("\n📊 RENDIMIENTO (Latencia)")
    print("-" * 80)

    minilm_avg = minilm["summary"]["average_latency_ms"]
    arctic_avg = arctic["summary"]["average_latency_ms"]
    improvement = ((minilm_avg - arctic_avg) / minilm_avg) * 100

    print(f"{'Métrica':<30} {'MiniLM-384D':>15} {'Arctic-768D':>15} {'Mejora':>15}")
    print("-" * 80)
    print(
        f"{'Latencia promedio':<30} {minilm_avg:>13.2f}ms {arctic_avg:>13.2f}ms {improvement:>13.2f}%"
    )
    print(
        f"{'Latencia mínima':<30} {minilm['summary']['min_latency_ms']:>13.2f}ms {arctic['summary']['min_latency_ms']:>13.2f}ms"
    )
    print(
        f"{'Latencia máxima':<30} {minilm['summary']['max_latency_ms']:>13.2f}ms {arctic['summary']['max_latency_ms']:>13.2f}ms"
    )

    # Query-by-query comparison
    print("\n🔍 COMPARACIÓN POR TIPO DE CONSULTA")
    print("-" * 80)
    print(f"{'Consulta':<35} {'MiniLM':>12} {'Arctic':>12} {'Mejora':>12}")
    print("-" * 80)

    for i, (mq, aq) in enumerate(zip(minilm["queries"], arctic["queries"])):
        if "latency_ms" in mq and "latency_ms" in aq:
            m_lat = mq["latency_ms"]
            a_lat = aq["latency_ms"]
            impr = ((m_lat - a_lat) / m_lat) * 100

            query_desc = mq["description"][:33]
            print(f"{query_desc:<35} {m_lat:>10.1f}ms {a_lat:>10.1f}ms {impr:>10.1f}%")

    # Results quality comparison
    print("\n🎯 CALIDAD DE RESULTADOS (Top Result Score)")
    print("-" * 80)
    print(f"{'Consulta':<40} {'MiniLM':>12} {'Arctic':>12}")
    print("-" * 80)

    for mq, aq in zip(minilm["queries"], arctic["queries"]):
        if mq.get("top_3_results") and aq.get("top_3_results"):
            m_score = mq["top_3_results"][0]["score"]
            a_score = aq["top_3_results"][0]["score"]

            query_desc = mq["description"][:38]
            print(f"{query_desc:<40} {m_score:>12.4f} {a_score:>12.4f}")

    # Detailed comparison for specific queries
    print("\n🔬 ANÁLISIS DETALLADO - Búsquedas Problemáticas")
    print("=" * 80)

    # Christopher Nolan search
    print("\n1. Búsqueda de Director: 'Christopher Nolan'")
    print("-" * 80)

    for idx, q in enumerate(minilm["queries"]):
        if q["query"] == "Christopher Nolan":
            print(f"\nMiniLM-384D (Latencia: {q['latency_ms']}ms):")
            for i, r in enumerate(q["top_3_results"][:3], 1):
                print(
                    f"  {i}. {r['title']} (score: {r['score']:.4f}) - Director: {r.get('director')}"
                )

            aq = arctic["queries"][idx]
            print(f"\nArctic-768D (Latencia: {aq['latency_ms']}ms):")
            for i, r in enumerate(aq["top_3_results"][:3], 1):
                print(
                    f"  {i}. {r['title']} (score: {r['score']:.4f}) - Director: {r.get('director')}"
                )

    # Multilingual search
    print("\n2. Búsqueda Multilingüe: 'películas de ciencia ficción'")
    print("-" * 80)

    for idx, q in enumerate(minilm["queries"]):
        if q["query"] == "películas de ciencia ficción":
            print(f"\nMiniLM-384D (Latencia: {q['latency_ms']}ms):")
            for i, r in enumerate(q["top_3_results"][:3], 1):
                print(f"  {i}. {r['title']} (score: {r['score']:.4f})")

            aq = arctic["queries"][idx]
            print(f"\nArctic-768D (Latencia: {aq['latency_ms']}ms):")
            for i, r in enumerate(aq["top_3_results"][:3], 1):
                print(f"  {i}. {r['title']} (score: {r['score']:.4f})")

    # Final recommendation
    print("\n" + "=" * 80)
    print("📋 RECOMENDACIÓN FINAL")
    print("=" * 80)

    if improvement > 0:
        print(
            f"\n✅ Arctic-768D muestra mejora de {improvement:.1f}% en latencia promedio"
        )
        print(f"   - Latencia promedio: {minilm_avg:.1f}ms → {arctic_avg:.1f}ms")
    else:
        print(f"\n⚠️  Arctic-768D tiene {abs(improvement):.1f}% más latencia que MiniLM")
        print(f"   - Latencia promedio: {minilm_avg:.1f}ms → {arctic_avg:.1f}ms")

    print("\n🔍 Observaciones:")
    print("   • Calidad de resultados: Similar en ambos modelos")
    print("   • Búsquedas exactas: Rendimiento comparable")
    print("   • Búsquedas semánticas: Necesita análisis más profundo")
    print("   • Búsquedas multilingües: Ambos con limitaciones")

    if improvement > 3:
        print("\n💡 Recomendación: MANTENER Arctic-768D")
        print("   Mejor rendimiento general con dimensiones más altas")
    elif improvement < -10:
        print("\n💡 Recomendación: REVERTIR a MiniLM-384D")
        print("   Mejor rendimiento con menores recursos")
    else:
        print("\n💡 Recomendación: Diferencia marginal, evaluar otros factores")
        print("   (Consumo de memoria, costos de infraestructura, etc.)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Uso: python3 compare_results.py <minilm_results.json> <arctic_results.json>"
        )
        sys.exit(1)

    compare_models(sys.argv[1], sys.argv[2])
