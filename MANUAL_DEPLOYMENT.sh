#!/bin/bash
# ⚠️ MANUAL DEPLOYMENT REQUIRED
# 
# The server has NOT auto-deployed the Arctic Embed + mxbai-rerank changes yet.
# Current models on server: MiniLM + mmarco (verified by test queries)
# 
# Execute these commands ON THE PRODUCTION SERVER to deploy new models:

set -e  # Exit on error

echo "🚀 DEPLOYING ARCTIC EMBED + mxbai-rerank"
echo "=========================================="
echo ""

# Step 1: Navigate to app directory
echo "📂 Step 1: Navigate to application directory"
cd /var/www/readyapi || {
    echo "❌ Error: Cannot find /var/www/readyapi"
    exit 1
}
echo "✅ Current directory: $(pwd)"
echo ""

# Step 2: Stop the service
echo "🛑 Step 2: Stop ReadyAPI service"
sudo systemctl stop readyapi || echo "⚠️ Service might not have been running"
sleep 2
echo "✅ Service stopped"
echo ""

# Step 3: Pull latest code
echo "📥 Step 3: Pull latest code from GitHub"
git fetch origin main
git reset --hard origin/main
echo "✅ Code updated"
git log --oneline -3
echo ""

# Step 4: Pre-download models (CRITICAL - first run takes 5-10 minutes)
echo "⏳ Step 4: Pre-downloading models (this takes 5-10 minutes on first run)"
echo "   - Arctic Embed (768D): ~500MB"
echo "   - mxbai-rerank (XSmall): ~100MB"
echo ""

python3 << 'PYTHON_SCRIPT'
import sys
print("Downloading Bi-Encoder: snowflake-arctic-embed-m-v1.5...")
from sentence_transformers import SentenceTransformer
try:
    model = SentenceTransformer('snowflake/snowflake-arctic-embed-m-v1.5')
    print(f"✅ Downloaded Arctic Embed ({model.get_sentence_embedding_dimension()}D)")
except Exception as e:
    print(f"❌ Error downloading Arctic: {e}")
    sys.exit(1)

print("\nDownloading Cross-Encoder: mxbai-rerank-xsmall-v1...")
from sentence_transformers.cross_encoders import CrossEncoder
try:
    reranker = CrossEncoder('mixedbread-ai/mxbai-rerank-xsmall-v1')
    print("✅ Downloaded mxbai-rerank")
except Exception as e:
    print(f"❌ Error downloading mxbai: {e}")
    sys.exit(1)

print("\n✅ All models downloaded successfully!")
PYTHON_SCRIPT

echo ""
echo ""

# Step 5: Rebuild ChromaDB indices
echo "🔨 Step 5: Rebuild ChromaDB indices (CRITICAL - 2-3 minutes)"
echo "   ⚠️ Old indices (384D vectors) incompatible with new embedder (768D)"
echo "   ⚠️ This step REMOVES old indices and rebuilds from movie data"
echo ""

python3 scripts/rebuild_index.py
if [ $? -eq 0 ]; then
    echo "✅ Indices rebuilt successfully"
else
    echo "❌ Error rebuilding indices"
    exit 1
fi
echo ""

# Step 6: Verify config
echo "🔍 Step 6: Verify configuration"
echo "Current EMBEDDING_MODEL:"
grep "EMBEDDING_MODEL" app/core/config.py | head -1
echo "Current RERANK_MODEL:"
grep "RERANK_MODEL" app/core/config.py | head -1
echo ""

# Step 7: Start service
echo "🚀 Step 7: Starting ReadyAPI service"
sudo systemctl start readyapi
sleep 3

if systemctl is-active --quiet readyapi; then
    echo "✅ Service started successfully"
else
    echo "❌ Service failed to start"
    echo "Checking logs..."
    sudo systemctl status readyapi
    exit 1
fi
echo ""

# Step 8: Verify service is responding
echo "🧪 Step 8: Verify service is responding"
echo "Making test request..."
RESPONSE=$(curl -s -X POST https://api.readyapi.net/api/v1/search/query \
    -H "X-API-Key: rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg" \
    -H "Content-Type: application/json" \
    -d '{"query":"test","top_k":1}')

if echo "$RESPONSE" | grep -q '"query"'; then
    echo "✅ Server responding correctly"
    echo "Sample response:"
    echo "$RESPONSE" | head -c 200
    echo "..."
else
    echo "❌ Server not responding properly"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""
echo ""

echo "═════════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "═════════════════════════════════════════"
echo ""
echo "Deployed Models:"
echo "  • Embedder: snowflake-arctic-embed-m-v1.5 (768D)"
echo "  • Reranker: mixedbread-ai/mxbai-rerank-xsmall-v1 (XSmall)"
echo ""
echo "Next Steps:"
echo "  1. From LOCAL machine, run evaluation:"
echo "     python3 scripts/evaluate_remote_server.py \\"
echo "       --api-key 'rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg' \\"
echo "       --output baseline_arctic_remote.json"
echo ""
echo "  2. Compare results:"
echo "     python3 scripts/compare_baselines.py \\"
echo "       --minilm baseline_minilm_remote.json \\"
echo "       --arctic baseline_arctic_remote.json \\"
echo "       --output comparison_report.md"
echo ""
