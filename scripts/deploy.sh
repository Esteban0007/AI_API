#!/bin/bash

# 🚀 Script de Deployment para api.readyapi.com
# Uso: ./scripts/deploy.sh api.readyapi.com tu_usuario

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
DOMAIN=${1:-api.readyapi.com}
SSH_USER=${2:-ubuntu}
SERVER="${SSH_USER}@${DOMAIN}"
APP_PATH="/var/www/readyapi"

echo -e "${GREEN}🚀 Deployment Script para ${DOMAIN}${NC}"
echo "=================================================="

# Verificaciones previas
echo -e "${YELLOW}[1/8] Verificando acceso SSH...${NC}"
if ssh -q "$SERVER" exit; then
    echo -e "${GREEN}✅ Acceso SSH OK${NC}"
else
    echo -e "${RED}❌ No hay acceso SSH a $SERVER${NC}"
    exit 1
fi

# Clonar repositorio
echo -e "${YELLOW}[2/8] Clonando repositorio...${NC}"
ssh "$SERVER" "mkdir -p /var/www && cd /var/www && \
    [ -d readyapi ] && echo 'Repo ya existe' || \
    git clone https://github.com/Esteban0007/AI_API.git readyapi"
echo -e "${GREEN}✅ Repositorio actualizado${NC}"

# Instalar Python y dependencias
echo -e "${YELLOW}[3/8] Instalando dependencias del sistema...${NC}"
ssh "$SERVER" "sudo apt update && \
    sudo apt install -y python3 python3-venv python3-pip \
    nginx certbot python3-certbot-nginx git"
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# Crear venv e instalar paquetes
echo -e "${YELLOW}[4/8] Creando entorno virtual e instalando paquetes Python...${NC}"
ssh "$SERVER" "cd $APP_PATH && \
    python3 -m venv venv && \
    source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn"
echo -e "${GREEN}✅ Entorno Python listo${NC}"

# Inicializar base de datos
echo -e "${YELLOW}[5/8] Inicializando base de datos...${NC}"
ssh "$SERVER" "cd $APP_PATH && \
    source venv/bin/activate && \
    python3 scripts/init_db.py"
echo -e "${GREEN}✅ Base de datos inicializada${NC}"

# Configurar Nginx
echo -e "${YELLOW}[6/8] Configurando Nginx...${NC}"
cat << 'EOF' > /tmp/nginx_config
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

sed "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /tmp/nginx_config > /tmp/nginx_config_final
scp /tmp/nginx_config_final "$SERVER:/tmp/readyapi_nginx"
ssh "$SERVER" "sudo mv /tmp/readyapi_nginx /etc/nginx/sites-available/readyapi && \
    sudo ln -sf /etc/nginx/sites-available/readyapi /etc/nginx/sites-enabled/ && \
    sudo rm -f /etc/nginx/sites-enabled/default && \
    sudo nginx -t && \
    sudo systemctl restart nginx"
echo -e "${GREEN}✅ Nginx configurado${NC}"

# Obtener certificado SSL
echo -e "${YELLOW}[7/8] Obtener certificado SSL (Let's Encrypt)...${NC}"
echo -e "${YELLOW}Ingresa tu email para las notificaciones de certificado:${NC}"
read -p "Email: " CERT_EMAIL
ssh "$SERVER" "sudo certbot --nginx -d $DOMAIN --non-interactive \
    --agree-tos --email $CERT_EMAIL --redirect"
echo -e "${GREEN}✅ Certificado SSL instalado${NC}"

# Configurar servicio systemd
echo -e "${YELLOW}[8/8] Configurando servicio systemd...${NC}"
cat << 'EOF' > /tmp/readyapi.service
[Unit]
Description=Semantic Search SaaS API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/readyapi
Environment="PATH=/var/www/readyapi/venv/bin"
ExecStart=/var/www/readyapi/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

scp /tmp/readyapi.service "$SERVER:/tmp/"
ssh "$SERVER" "sudo mv /tmp/readyapi.service /etc/systemd/system/ && \
    sudo chown -R www-data:www-data $APP_PATH && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable readyapi && \
    sudo systemctl start readyapi"
echo -e "${GREEN}✅ Servicio systemd configurado${NC}"

# Resumen final
echo ""
echo -e "${GREEN}=================================================="
echo "✅ ¡Deployment completado exitosamente!"
echo "=================================================${NC}"
echo ""
echo -e "${YELLOW}Tu API está disponible en:${NC}"
echo -e "${GREEN}  https://$DOMAIN${NC}"
echo ""
echo -e "${YELLOW}Documentación interactiva:${NC}"
echo -e "${GREEN}  https://$DOMAIN/api/docs${NC}"
echo ""
echo -e "${YELLOW}Pasos siguientes:${NC}"
echo "1. Actualiza tu .env con una ADMIN_API_KEY fuerte"
echo "2. Carga datos: python scripts/create_sample_data.py"
echo "3. Testa tu API:"
echo -e "   ${GREEN}curl https://$DOMAIN/health${NC}"
echo ""
echo -e "${YELLOW}Ver logs:${NC}"
echo -e "${GREEN}  ssh $SERVER 'sudo journalctl -u readyapi -f'${NC}"
echo ""
