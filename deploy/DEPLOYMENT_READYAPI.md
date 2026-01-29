# 🚀 Guía de Deployment HTTPS para readyapi.net

Esta guía está personalizada para tu dominio **readyapi.net**.

## 📋 Requisitos Verificados

- ✅ Dominio: readyapi.net
- ✅ Servidor propio
- ⚠️ Verificar: ¿El dominio apunta a la IP de tu servidor?
- ⚠️ Verificar: ¿Puertos 80 y 443 abiertos?

## 🎯 Pasos de Instalación

### 1. Conectar al Servidor y Clonar Repositorio

```bash
# Conectar vía SSH
ssh usuario@readyapi.net

# Ir al directorio web
cd /var/www

# Clonar el repositorio
sudo git clone https://github.com/Esteban0007/AI_API.git readyapi
cd readyapi

# Cambiar permisos
sudo chown -R $USER:$USER /var/www/readyapi
```

### 2. Configurar Entorno Python

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Para producción
```

### 3. Configurar Variables de Entorno

```bash
# Copiar configuración
cp .env.example .env

# Editar configuración
nano .env
```

**Configuración para readyapi.net:**

```env
# Server Configuration
DEBUG=false
HOST=127.0.0.1
PORT=8000

# Security
ENABLE_HTTPS=true
REQUIRE_HTTPS=true
ALLOWED_ORIGINS=https://api.readyapi.net,https://www.readyapi.net

# API Key (genera uno fuerte)
API_KEY_HEADER=X-API-Key
```

### 4. Cargar Datos Iniciales

```bash
# Generar documentos de ejemplo
python scripts/create_sample_data.py

# Cargar en base de datos vectorial
python scripts/load_json.py data/sample_documents.json
```

### 5. Configurar HTTPS con Let's Encrypt

```bash
# Dar permisos de ejecución al script
chmod +x deploy/setup_https.sh

# Ejecutar configuración automática
sudo deploy/setup_https.sh
```

**Cuando te pregunte:**

- **Dominio:** `readyapi.net` (sin www)
- **Email:** Tu email para notificaciones

El script:

1. Instalará Nginx y Certbot
2. Configurará Nginx como reverse proxy
3. Obtendrá certificado SSL gratuito de Let's Encrypt
4. Configurará renovación automática

### 6. Configurar Servicio Systemd

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/readyapi.service
```

**Contenido:**

```ini
[Unit]
Description=ReadyAPI - Semantic Search API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/readyapi
Environment="PATH=/var/www/readyapi/venv/bin"
ExecStart=/var/www/readyapi/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    app.main:app \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/readyapi/access.log \
    --error-logfile /var/log/readyapi/error.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/readyapi
sudo chown www-data:www-data /var/log/readyapi

# Activar servicio
sudo systemctl daemon-reload
sudo systemctl enable readyapi
sudo systemctl start readyapi
```

### 7. Verificar Funcionamiento

```bash
# Verificar servicio
sudo systemctl status readyapi

# Verificar Nginx
sudo systemctl status nginx

# Test HTTPS
curl https://readyapi.net/api/v1/search/health

# Verificar certificado
curl -vI https://readyapi.net 2>&1 | grep -i "subject\|issuer\|expire"
```

## 🧪 Pruebas de la API

### Health Check

```bash
curl https://readyapi.net/api/v1/search/health
```

### Búsqueda de Prueba

```bash
curl -X POST "https://readyapi.net/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-api-key" \
  -d '{
    "query": "machine learning algorithms",
    "top_k": 5
  }'
```

### Documentación Interactiva

Abre en tu navegador:

- **Swagger UI:** https://readyapi.net/api/docs
- **ReDoc:** https://readyapi.net/api/redoc

## 🔒 Checklist de Seguridad

```bash
# Ejecutar verificación de seguridad
bash deploy/security_check.sh
```

Verifica manualmente:

- [ ] HTTPS funcionando (candado verde en navegador)
- [ ] HTTP redirige a HTTPS
- [ ] Certificado válido de Let's Encrypt
- [ ] `DEBUG=false` en `.env`
- [ ] Firewall configurado (UFW)
- [ ] Solo puertos 22, 80, 443 abiertos
- [ ] API key configurado
- [ ] Logs funcionando

## 🛡️ Configurar Firewall

```bash
# Instalar UFW (si no está)
sudo apt install ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activar firewall
sudo ufw enable

# Verificar estado
sudo ufw status verbose
```

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Logs de la aplicación
sudo tail -f /var/log/readyapi/access.log
sudo tail -f /var/log/readyapi/error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs del sistema
sudo journalctl -u readyapi -f
```

### Verificar Rendimiento

```bash
# Estado del servidor
htop

# Conexiones activas
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :443

# Uso de disco
df -h
```

## 🔄 Mantenimiento

### Actualizar Código

```bash
cd /var/www/readyapi
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart readyapi
```

### Renovar Certificado SSL

```bash
# Test de renovación (sin renovar)
sudo certbot renew --dry-run

# Renovar manualmente (si es necesario)
sudo certbot renew
sudo systemctl reload nginx
```

### Backup de la Base de Datos

```bash
# Crear backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/chroma_db/

# Copiar a ubicación segura
scp backup-*.tar.gz usuario@servidor-backup:/backups/
```

## 🆘 Troubleshooting

### La API no responde

```bash
# Verificar servicio
sudo systemctl status readyapi
sudo journalctl -u readyapi -n 50

# Reiniciar servicio
sudo systemctl restart readyapi
```

### Error 502 Bad Gateway

```bash
# Verificar que la API esté corriendo
curl http://127.0.0.1:8000/api/v1/search/health

# Verificar configuración Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Certificado SSL expirado

```bash
# Ver fecha de expiración
sudo certbot certificates

# Forzar renovación
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

## 📞 URLs Importantes

- **API Producción:** https://readyapi.net
- **Documentación:** https://readyapi.net/api/docs
- **Health Check:** https://readyapi.net/api/v1/search/health
- **Repositorio:** https://github.com/Esteban0007/AI_API

## 🎯 Próximos Pasos Recomendados

1. **Implementar Rate Limiting:**
   - Instalar `slowapi` para limitar requests
   - Prevenir abuso de la API

2. **Configurar Monitoreo:**
   - Uptime Robot para monitoreo 24/7
   - Alertas por email si la API cae

3. **Optimizar Performance:**
   - Implementar Redis para caché
   - Aumentar workers de Gunicorn según carga

4. **Backups Automáticos:**
   - Cron job diario para backup de base de datos
   - Sincronización con almacenamiento externo

5. **CI/CD:**
   - GitHub Actions para deployment automático
   - Tests automáticos antes de deployment

---

**¿Necesitas ayuda con algún paso específico?** Estoy aquí para ayudarte.
