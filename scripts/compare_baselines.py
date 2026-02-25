#!/usr/bin/env python3
"""
Compare MiniLM baseline vs Arctic Embed results.
Generates a detailed comparison report.

Usage:
    python3 scripts/compare_baselines.py \
        --minilm baseline_minilm_remote.json \
        --arctic baseline_arctic_remote.json \
        --output comparison_report.md
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List


def load_json(path: str) -> Dict:
    """Load JSON report."""
    return json.loads(Path(path).read_text())


def calculate_stats(results: List[Dict]) -> Dict:
    """Calculate statistics from results."""
    valid = [r for r in results if "error" not in r]
    latencies = [r["latency_ms"] for r in valid]
    scores = []

    for r in valid:
        for res in r.get("top_results", []):
            if "score" in res:
                scores.append(res["score"])

    return {
        "count": len(valid),
        "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
        "min_latency_ms": min(latencies) if latencies else 0,
        "max_latency_ms": max(latencies) if latencies else 0,
        "avg_score": sum(scores) / len(scores) if scores else 0,
    }


def compare_category(minilm_cat: List[Dict], arctic_cat: List[Dict], cat_name: str):
    """Generate comparison for a single category."""
    minilm_stats = calculate_stats(minilm_cat)
    arctic_stats = calculate_stats(arctic_cat)

    latency_improvement = (
        ((minilm_stats["avg_latency_ms"] - arctic_stats["avg_latency_ms"]) /
         minilm_stats["avg_latency_ms"] * 100)
        if minilm_stats["avg_latency_ms"] > 0
        else 0
    )

    score_improvement = (
        ((arctic_stats["avg_score"] - minilm_stats["avg_score"]) /
         minilm_stats["avg_score"] * 100)
        if minilm_stats["avg_score"] > 0
        else 0
    )

    markdown = f"""
### {cat_name.upper()}

| Metric | MiniLM | Arctic | Change |
|--------|--------|--------|--------|
| Avg Latency | {minilm_stats["avg_latency_ms"]:.0f}ms | {arctic_stats["avg_latency_ms"]:.0f}ms | {latency_improvement:+.1f}% |
| Min Latency | {minilm_stats["min_latency_ms"]:.0f}ms | {arctic_stats["min_latency_ms"]:.0f}ms | |
| Max Latency | {minilm_stats["max_latency_ms"]:.0f}ms | {arctic_stats["max_latency_ms"]:.0f}ms | |
| Avg Score | {minilm_stats["avg_score"]:.4f} | {arctic_stats["avg_score"]:.4f} | {score_improvement:+.1f}% |
| Tests | {minilm_stats["count"]} | {arctic_stats["count"]} | |

#### Detailed Results
"""

    for i, (m, a) in enumerate(zip(minilm_cat, arctic_cat)):
        if "error" in m or "error" in a:
            markdown += f"\n**Query {i+1}:** {m.get('query', 'N/A')}"
            if "error" in m:
                markdown += f" ❌ MiniLM: {m['error']}"
            if "error" in a:
                markdown += f" ❌ Arctic: {a['error']}"
            continue

        m_latency = m["latency_ms"]
        a_latency = a["latency_ms"]
        latency_diff = ((m_latency - a_latency) / m_latency * 100)

        m_score = m["top_results"][0]["score"] if m["top_results"] else 0
        a_score = a["top_results"][0]["score"] if a["top_results"] else 0
        score_diff = ((a_score - m_score) / max(m_score, 0.001) * 100)

        emoji = "✅" if latency_diff > 0 else "⚠️"

        markdown += f"""
**Query {i+1}:** {m["query"]}
- MiniLM: {m_latency:.0f}ms, score {m_score:.4f}
- Arctic:  {a_latency:.0f}ms, score {a_score:.4f}
- Improvement: {emoji} {latency_diff:+.1f}% latency, {score_diff:+.1f}% score
"""

    return markdown


def main():
    parser = argparse.ArgumentParser(description="Compare model evaluation results")
    parser.add_argument("--minilm", required=True, help="MiniLM baseline JSON")
    parser.add_argument("--arctic", required=True, help="Arctic results JSON")
    parser.add_argument("--output", required=True, help="Output markdown report")
    args = parser.parse_args()

    minilm = load_json(args.minilm)
    arctic = load_json(args.arctic)

    # Generate report
    report = """# 📊 MODEL COMPARISON REPORT
## MiniLM + mmarco vs Arctic Embed + mxbai-rerank

**Generated:** 2026-02-25  
**Baseline:** MiniLM (sentence-transformers/all-MiniLM-L6-v2)  
**Challenger:** Arctic (snowflake/snowflake-arctic-embed-m-v1.5)  

---

## Executive Summary

"""

    # Overall stats
    for cat in ["semantic", "multilingual", "exact", "almost_exact"]:
        m_stats = calculate_stats(minilm[cat])
        a_stats = calculate_stats(arctic[cat])

        latency_imp = (
            ((m_stats["avg_latency_ms"] - a_stats["avg_latency_ms"]) /
             m_stats["avg_latency_ms"] * 100)
            if m_stats["avg_latency_ms"] > 0
            else 0
        )

        if latency_imp > 0:
            report += f"- **{cat}**: {latency_imp:.1f}% faster ⚡\n"
        else:
            report += f"- **{cat}**: {abs(latency_imp):.1f}% slower ⚠️\n"

    report += "\n---\n"

    # Detailed comparisons
    for cat in ["semantic", "multilingual", "exact", "almost_exact"]:
        report += compare_category(minilm[cat], arctic[cat], cat)

    # Save report
    Path(args.output).write_text(report)
    print(f"✅ Report saved to: {args.output}")
    print(report[:500] + "...\n")


if __name__ == "__main__":
    main()
