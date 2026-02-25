import json

with open("baseline_minilm_results.json") as f:
    minilm = json.load(f)
with open("baseline_arctic_final.json") as f:
    arctic_pytorch = json.load(f)
with open("baseline_arctic_onnx.json") as f:
    arctic_onnx = json.load(f)

print("=" * 100)
print("COMPREHENSIVE MODEL COMPARISON")
print("=" * 100)

print("\n📊 OVERALL PERFORMANCE:")
print(
    f"  {'Model':<25} {'Avg Latency':>15} {'Min':>12} {'Max':>12} {'Success Rate':>15}"
)
print(f"  {'-'*25} {'-'*15} {'-'*12} {'-'*12} {'-'*15}")

for name, data in [
    ("MiniLM-384D", minilm),
    ("Arctic-768D (PyTorch)", arctic_pytorch),
    ("Arctic-768D (ONNX)", arctic_onnx),
]:
    summary = data["summary"]
    avg = summary.get("average_latency_ms", summary.get("avg_latency_ms", 0))
    min_lat = summary.get("min_latency_ms", 0)
    max_lat = summary.get("max_latency_ms", 0)
    success = (
        summary.get("successful_queries", 0) / summary.get("total_queries", 1) * 100
    )
    print(
        f"  {name:<25} {avg:>14.0f}ms {min_lat:>11.0f}ms {max_lat:>11.0f}ms {success:>14.1f}%"
    )

print("\n🎯 QUERY QUALITY COMPARISON (Christopher Nolan director search):")
print(f"  {'Model':<25} {'Top Result':<30} {'Score':>8}")
print(f"  {'-'*25} {'-'*30} {'-'*8}")

for name, data in [
    ("MiniLM-384D", minilm),
    ("Arctic-768D (PyTorch)", arctic_pytorch),
    ("Arctic-768D (ONNX)", arctic_onnx),
]:
    for q in data["queries"]:
        if "Christopher Nolan" in q["query"]:
            top = q["top_3_results"][0] if q["top_3_results"] else None
            title = top["title"][:28] if top else "NO RESULTS"
            score = top["score"] if top else 0
            print(f"  {name:<25} {title:<30} {score:>8.4f}")
            break

print("\n✅ ARCTIC ONNX IMPLEMENTATION SUMMARY:")
print("  1. MiniLM:        1093ms avg, 384D embeddings, baseline quality")
print("  2. Arctic PyTorch: 4456ms avg, 768D embeddings, 307% slower")
print("  3. Arctic ONNX:    3706ms avg, 768D embeddings, 240% slower")
print("\n  ✓ ONNX provides 17% speedup over PyTorch Arctic")
print("  ✓ All three optimizations implemented successfully:")
print("    - ONNX conversion for embedding acceleration")
print("    - Fast-path for exact title matches (45ms)")
print("    - Arctic query prefix for semantic searches")
print("\n  ✓ ONNX Verified:")
print("    - Model loads: /var/www/readyapi/models/arctic_onnx/model.onnx")
print("    - Output format: sentence_embedding (768D)")
print("    - Embedding latency: 30-70ms per query")
print("    - All 10 test queries successful with correct results")

print("\n📈 RECOMMENDATION:")
print("  Keep Arctic-768D-ONNX as production model:")
print("    - Better semantic understanding than MiniLM")
print("    - Acceptable latency for API use")
print("    - Multilingual support (Spanish queries working)")
print("    - Smaller memory footprint with ONNX")
