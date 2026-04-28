#!/bin/bash
# Quick diagnostic script to find ReadyAPI code location on production server

SERVER="194.164.207.6"

echo "🔍 Searching for ReadyAPI code location..."
echo ""

ssh root@$SERVER << 'EOF'
    echo "Possible locations to check:"
    echo "================================"
    
    # Check common locations
    for dir in /root/readyapi /home/*/readyapi /opt/readyapi /var/www/readyapi /srv/readyapi; do
        if [ -d "$dir" ] && [ -f "$dir/app/main.py" ]; then
            echo "✅ Found at: $dir"
            echo "   Latest commits:"
            cd "$dir"
            git log --oneline -3
            echo ""
            echo "   Git status:"
            git status --short
            echo ""
        fi
    done
    
    # Check if running processes point to the location
    echo ""
    echo "Service information:"
    echo "================================"
    
    # Check systemd service
    if [ -f /etc/systemd/system/readyapi.service ]; then
        echo "Service file found at: /etc/systemd/system/readyapi.service"
        grep -E "(ExecStart|WorkingDirectory)" /etc/systemd/system/readyapi.service || true
    fi
    
    # Check running process
    echo ""
    echo "Running processes:"
    ps aux | grep -E "(gunicorn|uvicorn|python.*main)" | grep -v grep || echo "No FastAPI process found"
    
    # Check for git repositories
    echo ""
    echo "Git repositories found:"
    find / -name ".git" -path "*/readyapi/*" 2>/dev/null | head -3 || echo "None found"
EOF
