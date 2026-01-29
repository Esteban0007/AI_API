#!/bin/bash
# Security verification script

echo "🔐 Security Checklist for Semantic Search API"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check 1: .env file exists
echo "📋 Checking configuration..."
if [ -f ".env" ]; then
    check_pass ".env file exists"
    
    # Check DEBUG setting
    if grep -q "DEBUG=false" .env; then
        check_pass "DEBUG mode is OFF (production ready)"
    else
        check_warn "DEBUG mode is ON (recommended: DEBUG=false for production)"
    fi
    
    # Check HTTPS settings
    if grep -q "ENABLE_HTTPS=true" .env; then
        check_pass "HTTPS is enabled"
    else
        check_warn "HTTPS is disabled (recommended: ENABLE_HTTPS=true for production)"
    fi
else
    check_fail ".env file not found (copy from .env.example)"
fi

echo ""

# Check 2: Certificates (if HTTPS enabled)
echo "🔒 Checking SSL certificates..."
if [ -d "certs" ] && [ -f "certs/cert.pem" ]; then
    check_pass "SSL certificates found"
    
    # Check certificate expiration (if openssl available)
    if command -v openssl &> /dev/null; then
        CERT_EXPIRY=$(openssl x509 -enddate -noout -in certs/cert.pem | cut -d= -f2)
        echo "   Certificate expires: $CERT_EXPIRY"
    fi
else
    check_warn "No SSL certificates found (run scripts/run_server_https.py to generate)"
fi

echo ""

# Check 3: Gitignore security
echo "🔐 Checking .gitignore..."
if grep -q ".env" .gitignore && grep -q "certs/" .gitignore; then
    check_pass "Sensitive files are in .gitignore"
else
    check_fail "Update .gitignore to include .env and certs/"
fi

echo ""

# Check 4: Database security
echo "💾 Checking database..."
if [ -d "data/chroma_db" ]; then
    check_pass "Vector database exists"
    
    if grep -q "data/chroma_db/" .gitignore; then
        check_pass "Database directory in .gitignore"
    else
        check_fail "Add data/chroma_db/ to .gitignore"
    fi
else
    check_warn "Vector database not initialized"
fi

echo ""

# Check 5: Dependencies
echo "📦 Checking dependencies..."
if [ -d "venv" ] || [ -n "$VIRTUAL_ENV" ]; then
    check_pass "Virtual environment detected"
else
    check_warn "No virtual environment (recommended: python -m venv venv)"
fi

if [ -f "requirements.txt" ]; then
    check_pass "requirements.txt exists"
else
    check_fail "requirements.txt not found"
fi

echo ""

# Check 6: API key security
echo "🔑 Checking API security..."
if grep -q "X-API-Key" app/core/security.py; then
    check_pass "API key authentication implemented"
    check_warn "Remember to implement database validation in production"
else
    check_warn "Consider implementing API key authentication"
fi

echo ""

# Check 7: CORS configuration
echo "🌐 Checking CORS..."
if [ -f ".env" ]; then
    if grep -q "ALLOWED_ORIGINS" .env; then
        check_pass "CORS origins configured"
        ORIGINS=$(grep "ALLOWED_ORIGINS" .env)
        echo "   $ORIGINS"
    else
        check_warn "Set ALLOWED_ORIGINS in .env for production"
    fi
fi

echo ""

# Check 8: Nginx configuration (if exists)
echo "⚙️  Checking Nginx..."
if [ -f "/etc/nginx/sites-available/api" ]; then
    check_pass "Nginx configuration found"
    
    # Test nginx config
    if sudo nginx -t &> /dev/null; then
        check_pass "Nginx configuration is valid"
    else
        check_fail "Nginx configuration has errors (run: sudo nginx -t)"
    fi
else
    check_warn "Nginx not configured (optional if using Docker or direct HTTPS)"
fi

echo ""

# Check 9: Firewall
echo "🛡️  Checking firewall..."
if command -v ufw &> /dev/null; then
    if sudo ufw status | grep -q "Status: active"; then
        check_pass "UFW firewall is active"
        
        if sudo ufw status | grep -q "443/tcp"; then
            check_pass "HTTPS port (443) is open"
        else
            check_warn "HTTPS port not open (run: sudo ufw allow 443/tcp)"
        fi
    else
        check_warn "Firewall is not active"
    fi
else
    check_warn "UFW not installed (firewall check skipped)"
fi

echo ""

# Check 10: System service
echo "⚡ Checking systemd service..."
if systemctl list-units --type=service | grep -q "semantic-search"; then
    check_pass "Systemd service configured"
    
    if systemctl is-active --quiet semantic-search-api; then
        check_pass "Service is running"
    else
        check_warn "Service is not running (start with: sudo systemctl start semantic-search-api)"
    fi
else
    check_warn "Systemd service not configured (optional)"
fi

echo ""
echo "=============================================="
echo "🎯 Summary"
echo "=============================================="
echo ""
echo "Next steps for production:"
echo "  1. Set DEBUG=false in .env"
echo "  2. Configure HTTPS with Let's Encrypt"
echo "  3. Set up proper API key validation"
echo "  4. Configure firewall (ports 80, 443, 22 only)"
echo "  5. Set up monitoring and logging"
echo "  6. Configure automatic backups"
echo ""
echo "For detailed HTTPS setup, see:"
echo "  deploy/HTTPS_GUIDE.md"
echo ""
