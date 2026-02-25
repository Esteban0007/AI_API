#!/bin/bash
# DEPLOYMENT SCRIPT FOR PRODUCTION SERVER
# Run this on the server machine to deploy Arctic Embed + mxbai-rerank

echo "🚀 DEPLOYMENT: Arctic Embed + mxbai-rerank"
echo "=============================================="

# Navigate to application directory
cd /var/www/readyapi || exit 1

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# The models will be auto-downloaded on first use by HuggingFace
# But we can pre-download them to avoid delays during first request
echo "⏳ Pre-downloading models (this may take 5-10 minutes on first run)..."
python3 -c "
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoders import CrossEncoder

print('Downloading Bi-Encoder (Arctic Embed)...')
SentenceTransformer('snowflake/snowflake-arctic-embed-m-v1.5')

print('Downloading Cross-Encoder (mxbai-rerank)...')
CrossEncoder('mixedbread-ai/mxbai-rerank-xsmall-v1')

print('✅ Models downloaded successfully')
"

# CRITICAL: Rebuild ChromaDB indices
# The new embedder uses 768D vectors instead of 384D
# Old indices must be recreated
echo ""
echo "⚠️  CRITICAL: Rebuilding ChromaDB indices..."
echo "   Old indices (384D) incompatible with new embedder (768D)"
python3 scripts/rebuild_index.py

# Restart the service
echo ""
echo "🔄 Restarting ReadyAPI service..."
systemctl restart readyapi

# Verify service is running
sleep 2
if systemctl is-active --quiet readyapi; then
    echo "✅ Service restarted successfully"
else
    echo "❌ Service failed to start"
    systemctl status readyapi
    exit 1
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "   Embedder: snowflake/snowflake-arctic-embed-m-v1.5 (768D)"
echo "   Reranker: mixedbread-ai/mxbai-rerank-xsmall-v1"
echo ""
echo "Next: Run evaluation tests to verify improvements"
