# 🔐 HTTPS Configuration Guide

Guía paso a paso para configurar HTTPS en tu API de búsqueda semántica.

## 📋 Opciones de Configuración

### Opción 1: Producción con Let's Encrypt (RECOMENDADO)

**Para:** Servidores públicos con dominio propio
**Certificado:** Gratuito y renovable automáticamente
**Dificultad:** Media

### Opción 2: Desarrollo Local con SSL Auto-firmado

**Para:** Testing local HTTPS
**Certificado:** Auto-generado (no válido públicamente)
**Dificultad:** Fácil

### Opción 3: Docker + Nginx + Let's Encrypt

**Para:** Deployment containerizado
**Certificado:** Gratuito y renovable
**Dificultad:** Media-Alta

---

## 🚀 Opción 1: Producción con Let's Encrypt

### Requisitos

- ✅ Servidor Linux (Ubuntu/Debian recomendado)
- ✅ Dominio apuntando a tu servidor (ej: `api.tudominio.com`)
- ✅ Puertos 80 y 443 abiertos en firewall
- ✅ Acceso root/sudo

### Paso 1: Preparar el Servidor

```bash
# Conectar a tu servidor
ssh usuario@tu-servidor.com

# Clonar el repositorio
cd /var/www
git clone https://github.com/Esteban0007/AI_API.git
cd AI_API

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar configuración de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

Configuración recomendada para producción:

```env
DEBUG=false
HOST=127.0.0.1  # Solo acceso local (Nginx hace proxy)
PORT=8000
ENABLE_HTTPS=true
REQUIRE_HTTPS=true
ALLOWED_ORIGINS=["https://api.tudominio.com"]
```

### Paso 3: Ejecutar Script de Configuración HTTPS

```bash
# Dar permisos de ejecución
chmod +x deploy/setup_https.sh

# Ejecutar (requiere sudo)
sudo deploy/setup_https.sh
```

El script te preguntará:

- **Dominio:** `api.tudominio.com`
- **Email:** `tu@email.com` (para notificaciones de renovación)

### Paso 4: Configurar Systemd para Auto-inicio

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/semantic-search-api.service
```

Contenido:

```ini
[Unit]
Description=Semantic Search FastAPI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/AI_API
Environment="PATH=/var/www/AI_API/venv/bin"
ExecStart=/var/www/AI_API/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar el servicio:

```bash
sudo systemctl daemon-reload
sudo systemctl enable semantic-search-api
sudo systemctl start semantic-search-api
sudo systemctl status semantic-search-api
```

### Paso 5: Verificar

```bash
# Verificar HTTPS
curl https://api.tudominio.com/api/v1/search/health

# Verificar redirección HTTP → HTTPS
curl -I http://api.tudominio.com
# Debería devolver: HTTP/1.1 301 Moved Permanently
```

### Renovación Automática

Let's Encrypt configura renovación automática. Verifica:

```bash
# Test de renovación (no renueva realmente)
sudo certbot renew --dry-run

# Ver timer de renovación
sudo systemctl status certbot.timer
```

---

## 💻 Opción 2: Desarrollo Local (SSL Auto-firmado)

### Para Testing Local de HTTPS

```bash
# Generar certificado y arrancar servidor
python scripts/run_server_https.py
```

Esto:

1. Genera certificado auto-firmado en `certs/`
2. Inicia servidor en `https://localhost:8000`
3. Muestra warning del navegador (normal, cert no es de CA confiable)

### Acceder a la API

1. Abre `https://localhost:8000/api/docs`
2. El navegador mostrará warning de seguridad
3. Click en "Avanzado" → "Continuar a localhost"
4. ✅ Ya puedes probar la API con HTTPS

**⚠️ IMPORTANTE:** Solo para desarrollo. NUNCA uses certificados auto-firmados en producción.

---

## 🐳 Opción 3: Docker + Nginx + Let's Encrypt

### Paso 1: Preparar Configuración

Edita `deploy/docker-compose.https.yml`:

```yaml
# Línea 31-32: Cambia el dominio y email
command: certonly --webroot --webroot-path=/var/www/certbot --email TU_EMAIL --agree-tos --no-eff-email -d TU_DOMINIO
```

### Paso 2: Levantar Servicios

```bash
# Primera vez (obtener certificado)
docker-compose -f deploy/docker-compose.https.yml up -d certbot

# Esperar a que certbot termine
sleep 10

# Levantar todos los servicios
docker-compose -f deploy/docker-compose.https.yml up -d
```

### Paso 3: Renovación Automática

Agregar cron job:

```bash
# Editar crontab
crontab -e

# Agregar renovación semanal
0 0 * * 0 docker-compose -f /ruta/deploy/docker-compose.https.yml run certbot renew && docker-compose -f /ruta/deploy/docker-compose.https.yml restart nginx
```

---

## 🔒 Headers de Seguridad (Ya Configurados)

El archivo `deploy/nginx.conf` incluye:

```nginx
# HSTS - Fuerza HTTPS por 2 años
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload

# Previene MIME sniffing
X-Content-Type-Options: nosniff

# Previene clickjacking
X-Frame-Options: DENY

# XSS Protection
X-XSS-Protection: 1; mode=block
```

---

## ✅ Checklist de Seguridad Post-Configuración

- [ ] HTTPS funcionando correctamente
- [ ] HTTP redirige automáticamente a HTTPS
- [ ] Certificado válido (no auto-firmado en producción)
- [ ] `DEBUG=false` en `.env`
- [ ] `ALLOWED_ORIGINS` actualizado con tu dominio HTTPS
- [ ] Firewall configurado (solo puertos 80, 443, 22)
- [ ] Auto-renovación de certificado configurada
- [ ] Logs monitoreados (`/var/log/nginx/error.log`)

---

## 🛠️ Troubleshooting

### Error: "Certificate verification failed"

```bash
# Verificar configuración Nginx
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

### Error: "Port 443 already in use"

```bash
# Ver qué está usando el puerto
sudo lsof -i :443
sudo netstat -tulpn | grep :443
```

### Renovación de certificado falla

```bash
# Ver logs de certbot
sudo journalctl -u certbot

# Renovar manualmente
sudo certbot renew --force-renewal
```

### Browser muestra "Not Secure"

1. Verifica que el certificado sea de Let's Encrypt (no auto-firmado)
2. Verifica que el dominio coincida exactamente
3. Limpia caché del navegador

---

## 📚 Recursos Adicionales

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx SSL Configuration](https://ssl-config.mozilla.org/)
- [FastAPI HTTPS Guide](https://fastapi.tiangolo.com/deployment/https/)

---

## 🆘 ¿Necesitas Ayuda?

Si encuentras problemas:

1. Revisa los logs: `sudo journalctl -u semantic-search-api`
2. Verifica Nginx: `sudo nginx -t`
3. Test de conectividad: `curl -v https://tu-dominio.com`
