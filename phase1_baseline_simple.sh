#!/bin/bash
# FASE 1: BASELINE EVALUATION - Test current server (MiniLM + mmarco)

API_URL="https://api.readyapi.net/api/v1/search/query"
API_KEY="rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"
OUTPUT_FILE="phase1_baseline_results.txt"

echo "🔬 PHASE 1: BASELINE EVALUATION (MiniLM + mmarco)"
echo "════════════════════════════════════════════════════════════════" | tee "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# Function to run a test and save result
run_test() {
    local category=$1
    local query=$2
    
    echo "Testing [$category]: \"$query\"" | tee -a "$OUTPUT_FILE"
    
    curl -s "$API_URL" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "{\"query\":\"$query\",\"top_k\":3}" | tee -a "$OUTPUT_FILE"
    
    echo "" | tee -a "$OUTPUT_FILE"
    sleep 0.5
}

echo "📊 SEMANTIC Tests:" | tee -a "$OUTPUT_FILE"
run_test "semantic" "movies about artificial intelligence"
run_test "semantic" "existential crisis in space"

echo "" | tee -a "$OUTPUT_FILE"
echo "🌍 MULTILINGUAL Tests:" | tee -a "$OUTPUT_FILE"
run_test "multilingual" "películas de robótica"
run_test "multilingual" "drama amoroso"

echo "" | tee -a "$OUTPUT_FILE"
echo "🎯 EXACT TITLE Tests:" | tee -a "$OUTPUT_FILE"
run_test "exact" "Avatar"
run_test "exact" "A Woman Scorned"

echo "" | tee -a "$OUTPUT_FILE"
echo "🔍 ALMOST-EXACT Tests:" | tee -a "$OUTPUT_FILE"
run_test "almost_exact" "Woman Scorned"
run_test "almost_exact" "Shawshank Redemption"

echo "" | tee -a "$OUTPUT_FILE"
echo "════════════════════════════════════════════════════════════════" | tee -a "$OUTPUT_FILE"
echo "✅ BASELINE COMPLETE - Results saved to: $OUTPUT_FILE" | tee -a "$OUTPUT_FILE"
