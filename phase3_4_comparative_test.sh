#!/bin/bash
# PHASE 3 & 4: COMPARATIVE TEST (A/B Test) 
# Runs identical tests and compares baseline vs new models

API_URL="https://api.readyapi.net/api/v1/search/query"
API_KEY="rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

OUTPUT_FILE="phase3_4_comparative.md"

echo "🔬 PHASE 3 & 4: COMPARATIVE TEST (A/B Testing)"
echo "════════════════════════════════════════════════════════════════" | tee "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"
echo "This will run identical queries and record latencies for comparison" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# Test data (same as Phase 1)
declare -A tests
tests[semantic_ai]="movies about artificial intelligence"
tests[semantic_space]="existential crisis in space"
tests[multilingual_robot]="películas de robótica"
tests[multilingual_drama]="drama amoroso"
tests[exact_avatar]="Avatar"
tests[exact_woman]="A Woman Scorned"
tests[almost_woman]="Woman Scorned"
tests[almost_shawshank]="Shawshank Redemption"

# Function to run test
run_query() {
    local key=$1
    local query=$2
    
    result=$(curl -s "$API_URL" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "{\"query\":\"$query\",\"top_k\":1}" 2>/dev/null)
    
    title=$(echo "$result" | jq -r '.results[0].title // "ERROR"' 2>/dev/null)
    score=$(echo "$result" | jq -r '.results[0].score // 0' 2>/dev/null)
    latency=$(echo "$result" | jq -r '.execution_time_ms // 0' 2>/dev/null)
    
    echo "$key|$query|$title|$score|$latency"
}

# Collect results
echo "Running tests (8 queries)..." | tee -a "$OUTPUT_FILE"
sleep 1

declare -a results
for key in "${!tests[@]}"; do
    echo "  Testing: $key..." >&2
    results+=("$(run_query "$key" "${tests[$key]}")")
    sleep 0.3
done

# Create markdown comparison table
{
    echo ""
    echo "# Comparative Results"
    echo ""
    echo "| Test | Query | Result | Score | Latency (ms) |"
    echo "|------|-------|--------|-------|--------------|"
    
    for r in "${results[@]}"; do
        IFS='|' read -r key query title score latency <<< "$r"
        printf "| %s | %s | %s | %.4f | %.0f |\n" "$key" "$query" "$title" "$score" "$latency"
    done
    
    echo ""
    echo "## Analysis"
    echo ""
    
    # Calculate stats
    scores=$(echo "${results[@]}" | tr ' ' '\n' | cut -d'|' -f4 | paste -sd+ | bc -l)
    latencies=$(echo "${results[@]}" | tr ' ' '\n' | cut -d'|' -f5 | paste -sd+ | bc -l)
    
    echo "- Total tests: ${#results[@]}"
    echo "- Average score: $(echo "scale=4; $scores / ${#results[@]}" | bc)"
    echo "- Average latency: $(echo "scale=0; $latencies / ${#results[@]}" | bc)ms"
    
} >> "$OUTPUT_FILE"

cat "$OUTPUT_FILE"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ Comparative test saved to: $OUTPUT_FILE"
echo ""
echo "📊 TO COMPARE WITH BASELINE:"
echo "   1. Note the latencies above"
echo "   2. Compare with PHASE1_BASELINE_ANALYSIS.md"
echo "   3. Calculate latency improvements"
echo ""
