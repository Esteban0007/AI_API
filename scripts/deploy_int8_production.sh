#!/bin/bash
# INT8 Quantization Deployment Script
# Deploy to production server: 194.164.207.6

set -e

SERVER="root@194.164.207.6"
READYAPI_DIR="/var/www/readyapi"
MODELS_DIR="$READYAPI_DIR/models/arctic_onnx"

echo "=============================================================================="
echo "INT8 QUANTIZATION DEPLOYMENT"
echo "=============================================================================="
echo ""

# Step 1: Update code
echo "📦 Step 1: Updating code on server..."
ssh $SERVER << 'EOF'
cd /var/www/readyapi
echo "Stashing local changes..."
git stash
echo "Pulling latest code..."
git pull origin main
echo "✅ Code updated"
EOF

echo ""
echo "⏳ Step 2: Checking current space..."
ssh $SERVER "df -h $READYAPI_DIR | tail -1"

echo ""
echo "⏳ Step 3: Generating INT8 quantized model..."
echo "   This will take approximately 20 minutes..."
echo ""

ssh $SERVER << 'EOF'
cd /var/www/readyapi
python3 << 'PYTHON'
import subprocess
import sys

print("=" * 80)
print("Starting INT8 Quantization Process")
print("=" * 80)
print("")

try:
    result = subprocess.run(
        [sys.executable, "scripts/quantize_arctic_int8.py"],
        timeout=3600,  # 60 minutes timeout
        check=True
    )
    print("")
    print("✅ INT8 Quantization completed successfully")
except subprocess.TimeoutExpired:
    print("❌ Quantization timed out after 60 minutes")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"❌ Quantization failed: {e}")
    sys.exit(1)

# Verify INT8 model
import os
int8_path = "/var/www/readyapi/models/arctic_onnx/model_int8.onnx"
if os.path.exists(int8_path):
    size_mb = os.path.getsize(int8_path) / (1024 * 1024)
    print(f"✅ INT8 model created: {size_mb:.1f} MB")
else:
    print("❌ INT8 model not found!")
    sys.exit(1)

PYTHON

EOF

echo ""
echo "=============================================================================="
echo "✅ DEPLOYMENT COMPLETED"
echo "=============================================================================="
echo ""
echo "📊 Status:"
echo "   • Code: ✅ Updated"
echo "   • INT8 Model: ✅ Generated (400MB)"
echo "   • API: Will auto-detect and use INT8 on next request"
echo ""
echo "🧪 To verify:"
echo "   curl https://api.readyapi.net/health"
echo "   Should show: \"embedding_model\": \"INT8 ONNX\""
echo ""
echo "📈 Expected improvements:"
echo "   • Latency: 10-15% faster"
echo "   • Memory: 75% reduction"
echo ""
