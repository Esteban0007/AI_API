#!/bin/bash
# Deploy script for ReadyAPI production server

set -e

SERVER_IP="194.164.207.6"
SERVER_USER="root"
CODE_DIR="/root/readyapi"  # Adjust if different
VENV_DIR="$CODE_DIR/venv"

echo "=========================================="
echo "ReadyAPI Production Deployment Script"
echo "=========================================="

# Step 1: Verify local changes are committed
echo ""
echo "Step 1: Checking local git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: You have uncommitted changes. Please commit them first:"
    git status
    exit 1
else
    echo "✅ Working directory is clean"
fi

# Step 2: Verify main branch is up to date
echo ""
echo "Step 2: Checking if main branch is up to date..."
CURRENT=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$CURRENT" != "$REMOTE" ]; then
    echo "⚠️  Local and remote differ. Syncing..."
    git fetch origin
    git merge origin/main
fi
LATEST_COMMIT=$(git log -1 --oneline)
echo "✅ Latest commit: $LATEST_COMMIT"

# Step 3: SSH into server and deploy
echo ""
echo "Step 3: Deploying to production server..."
ssh -o ConnectTimeout=10 "$SERVER_USER@$SERVER_IP" << 'EOF'
    set -e
    
    echo ""
    echo "📍 Connected to production server"
    
    # Navigate to code directory
    if [ ! -d "/root/readyapi" ]; then
        echo "❌ Error: Code directory /root/readyapi not found"
        exit 1
    fi
    
    cd /root/readyapi
    echo "📂 Working directory: $(pwd)"
    
    # Step 4: Pull latest code
    echo ""
    echo "🔄 Pulling latest code from main branch..."
    git fetch origin
    git pull origin main
    echo "✅ Code updated"
    
    # Step 5: Check for changes
    echo ""
    echo "📋 Changes deployed:"
    git log -1 --stat
    
    # Step 6: Restart the service
    echo ""
    echo "🔄 Restarting ReadyAPI service..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl restart readyapi
        sleep 3
        sudo systemctl status readyapi --no-pager | head -10
    else
        echo "⚠️  systemctl not available, trying supervisorctl..."
        sudo supervisorctl restart readyapi || echo "⚠️  Manual restart needed"
    fi
    
    echo ""
    echo "✅ Deployment complete!"
EOF

# Step 4: Verify deployment
echo ""
echo "Step 4: Verifying deployment..."
echo ""
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://readyapi.net/health)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "✅ Health check passed (HTTP $HEALTH_RESPONSE)"
else
    echo "⚠️  Health check returned HTTP $HEALTH_RESPONSE (expected 200)"
fi

echo ""
echo "=========================================="
echo "✅ Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Visit https://readyapi.net/register and create a test account"
echo "2. Confirm your email"
echo "3. Log in and verify the dashboard loads"
echo ""
