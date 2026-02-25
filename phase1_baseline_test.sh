#!/bin/bash
# FASE 1: BASELINE EVALUATION - Test current server (MiniLM + mmarco)
# Records latency and result quality for all test categories

API_URL="https://api.readyapi.net/api/v1/search/query"
API_KEY="rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"
OUTPUT_FILE="phase1_baseline.json"

echo "🔬 PHASE 1: BASELINE EVALUATION (MiniLM + mmarco)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to run a test
run_test() {
    local category=$1
    local query=$2
    local top_k=${3:-5}
    
    result=$(curl -s "$API_URL" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "{\"query\":\"$query\",\"top_k\":$top_k}" 2>/dev/null)
    
    # Extract data
    title=$(echo "$result" | jq -r '.results[0].title // "NO_RESULT"' 2>/dev/null)
    score=$(echo "$result" | jq -r '.results[0].score // 0' 2>/dev/null)
    latency=$(echo "$result" | jq -r '.execution_time_ms // 0' 2>/dev/null)
    
    echo "  [$category] \"$query\""
    echo "    → Result: $title | Score: $score | Latency: ${latency}ms"
    
    # Return as JSON for accumulation
    echo "{\"category\":\"$category\",\"query\":\"$query\",\"title\":\"$title\",\"score\":$score,\"latency_ms\":$latency}"
}

# Arrays to collect all results
declare -a results

echo "📊 SEMANTIC UNDERSTANDING Tests:"
echo "-"
results+=("$(run_test 'semantic' 'movies about the struggle of artificial intelligence')")
results+=("$(run_test 'semantic' 'existential crisis in space')")
results+=("$(run_test 'semantic' 'a lonely astronaut facing despair')")
results+=("$(run_test 'semantic' 'the ethics of creating conscious machines')")

echo ""
echo "🌍 MULTILINGUAL Tests:"
echo "-"
results+=("$(run_test 'multilingual' 'películas de robótica')")
results+=("$(run_test 'multilingual' 'drama amoroso')")
results+=("$(run_test 'multilingual' 'film d'\''animazione')")
results+=("$(run_test 'multilingual' 'avventura spaziale')")

echo ""
echo "🎯 EXACT TITLE MATCH Tests:"
echo "-"
results+=("$(run_test 'exact' 'A Woman Scorned' 1)")
results+=("$(run_test 'exact' 'Avatar' 1)")
results+=("$(run_test 'exact' 'The Shawshank Redemption' 1)")

echo ""
echo "🔍 ALMOST-EXACT TITLE MATCH Tests:"
echo "-"
results+=("$(run_test 'almost_exact' 'A Woman Scorne')")
results+=("$(run_test 'almost_exact' 'Woman Scorned')")
results+=("$(run_test 'almost_exact' 'Shawshank Redemption')")

# Save results as JSON
echo ""
echo "💾 Saving results to $OUTPUT_FILE..."

# Create JSON output with jq
{
    echo "["
    for i in "${!results[@]}"; do
        echo "${results[$i]}"
        if [ $i -lt $((${#results[@]} - 1)) ]; then
            echo ","
        fi
    done
    echo "]"
} > "$OUTPUT_FILE"

# Print summary
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ BASELINE COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Results saved to: $OUTPUT_FILE"
echo ""

# Calculate statistics
avg_latency=$(cat "$OUTPUT_FILE" | jq '[.[].latency_ms] | add / length' 2>/dev/null)
max_latency=$(cat "$OUTPUT_FILE" | jq '[.[].latency_ms] | max' 2>/dev/null)
min_latency=$(cat "$OUTPUT_FILE" | jq '[.[].latency_ms] | min' 2>/dev/null)

echo "📈 Statistics:"
echo "  Average latency: ${avg_latency}ms"
echo "  Max latency: ${max_latency}ms"
echo "  Min latency: ${min_latency}ms"
echo ""
echo "Use this data as BASELINE to compare with new models."
echo ""
