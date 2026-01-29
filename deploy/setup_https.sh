#!/bin/bash
# Automated HTTPS setup with Let's Encrypt

set -e

echo "🔐 HTTPS Setup Script for Semantic Search API"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo ./setup_https.sh)"
    exit 1
fi

# Prompt for domain
read -p "📝 Enter your domain name (e.g., api.example.com): " DOMAIN
read -p "📧 Enter your email for Let's Encrypt: " EMAIL

echo ""
echo "📋 Configuration:"
echo "   Domain: $DOMAIN"
echo "   Email: $EMAIL"
echo ""
read -p "Continue? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "❌ Cancelled"
    exit 1
fi

echo ""
echo "📦 Step 1: Installing dependencies..."
apt update
apt install -y nginx certbot python3-certbot-nginx

echo ""
echo "🔧 Step 2: Configuring Nginx..."
# Backup existing config
if [ -f /etc/nginx/sites-available/default ]; then
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
fi

# Replace domain in nginx config
sed "s/tu-dominio.com/$DOMAIN/g" nginx.conf > /etc/nginx/sites-available/api
ln -sf /etc/nginx/sites-available/api /etc/nginx/sites-enabled/api

# Remove default site
rm -f /etc/nginx/sites-enabled/default

echo ""
echo "✅ Step 3: Testing Nginx configuration..."
nginx -t

echo ""
echo "🔄 Step 4: Restarting Nginx..."
systemctl restart nginx
systemctl enable nginx

echo ""
echo "🔒 Step 5: Obtaining SSL certificate from Let's Encrypt..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

echo ""
echo "⏰ Step 6: Setting up auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "✅ HTTPS setup complete!"
echo ""
echo "🌐 Your API is now available at:"
echo "   https://$DOMAIN"
echo "   https://$DOMAIN/api/docs"
echo ""
echo "📝 Next steps:"
echo "   1. Update your .env file: ALLOWED_ORIGINS=[\"https://$DOMAIN\"]"
echo "   2. Set DEBUG=false in .env"
echo "   3. Restart your FastAPI app"
echo ""
echo "🔄 Certificate will auto-renew. Test with:"
echo "   certbot renew --dry-run"
