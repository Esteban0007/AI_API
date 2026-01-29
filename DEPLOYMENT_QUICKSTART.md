# 🚀 Deployment a api.readyapi.com - Guía Rápida

## Prerequisitos

Antes de empezar, necesitas:

1. **Acceso SSH al servidor**

   ```bash
   ssh usuario@api.readyapi.com
   # o ssh usuario@IP_DEL_SERVIDOR
   ```

2. **Dominio DNS apuntando al servidor**
   - `api.readyapi.com` debe resolver a la IP del servidor
   - Puertos 80 y 443 deben estar abiertos

3. **Sistema Operativo recomendado**
   - Ubuntu 20.04 LTS o superior
   - Debian 10 o superior

## Pasos de Deployment

### Paso 1: Conectar al Servidor

```bash
# Conectar vía SSH
ssh usuario@api.readyapi.com

# Actualizar el sistema
sudo apt update && sudo apt upgrade -y
```

### Paso 2: Clonar el Repositorio

```bash
# Crear directorio para la app
mkdir -p /var/www
cd /var/www

# Clonar desde GitHub
git clone https://github.com/Esteban0007/AI_API.git readyapi
cd readyapi

# Cambiar permisos
sudo chown -R $USER:$USER .
```

### Paso 3: Instalar Dependencias

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar requisitos
pip install -r requirements.txt

# Instalar gunicorn para producción
pip install gunicorn
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar configuración de ejemplo
cp .env.example .env

# Editar con tus valores
nano .env
```

**Valores importantes para producción:**

```env
# Server
DEBUG=false
HOST=127.0.0.1
PORT=8000

# Security
ENABLE_HTTPS=true
ALLOWED_ORIGINS=https://api.readyapi.com

# Admin API Key (generar uno fuerte)
ADMIN_API_KEY=rapi_[TU_CLAVE_FUERTE_AQUI]
```

Para generar una clave fuerte:

```bash
python3 -c "import secrets; print('rapi_' + secrets.token_urlsafe(40))"
```

### Paso 5: Inicializar Base de Datos

```bash
# Activar entorno
source venv/bin/activate

# Inicializar DB
python3 scripts/init_db.py

# Crear documentos de ejemplo (opcional)
python3 scripts/create_sample_data.py
python3 scripts/load_json.py data/sample_documents.json
```

### Paso 6: Instalar y Configurar Nginx + HTTPS

```bash
# Instalar Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Crear archivo de configuración Nginx
sudo nano /etc/nginx/sites-available/readyapi
```

Pega esta configuración:

```nginx
server {
    listen 80;
    server_name api.readyapi.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Para WebSockets (si los usas)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/readyapi /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Paso 7: Obtener Certificado SSL con Let's Encrypt

```bash
# Obtener certificado
sudo certbot --nginx -d api.readyapi.com

# Cuando pregunte por email, ingresa tu correo
# Acepta los términos de servicio
# Elige para auto-renovar el certificado
```

El certificado se renovará automáticamente.

### Paso 8: Configurar Systemd para la App

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/readyapi.service
```

Pega esto:

```ini
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
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`

```bash
# Cambiar permisos del directorio a www-data
sudo chown -R www-data:www-data /var/www/readyapi

# Habilitar y iniciar servicio
sudo systemctl enable readyapi
sudo systemctl start readyapi

# Ver estado
sudo systemctl status readyapi
```

### Paso 9: Verificar que Todo Funciona

```bash
# Desde tu máquina local, probar:
curl https://api.readyapi.com/health

# Con autenticación admin:
curl -H "X-API-Key: TU_ADMIN_KEY" \
  https://api.readyapi.com/api/v1/users/me

# Ver documentación:
# https://api.readyapi.com/api/docs
```

## Monitoreo y Logs

```bash
# Ver logs en tiempo real
sudo journalctl -u readyapi -f

# Ver estado del servicio
sudo systemctl status readyapi

# Reiniciar servicio
sudo systemctl restart readyapi
```

## Actualizaciones Futuras

```bash
# En el servidor:
cd /var/www/readyapi
source venv/bin/activate

# Actualizar código
git pull origin main

# Instalar nuevas dependencias (si las hay)
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart readyapi
```

## Troubleshooting

### El sitio no carga (502 Bad Gateway)

```bash
# Verificar que la app está ejecutándose
sudo systemctl status readyapi

# Ver los logs
sudo journalctl -u readyapi -n 50
```

### Certificado SSL no funciona

```bash
# Renovar manual
sudo certbot renew --dry-run

# O renovar definitivo
sudo certbot renew
```

### Cambiar ADMIN_API_KEY

```bash
# En el servidor
nano /var/www/readyapi/.env

# Cambiar ADMIN_API_KEY
# Luego:
sudo systemctl restart readyapi
```

## Seguridad Adicional (Opcional)

### Firewall

```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Rate Limiting en Nginx

Añade a `/etc/nginx/sites-available/readyapi`:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

server {
    # ...
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        # resto de configuración...
    }
}
```

## Soporte

Para problemas, verifica:

1. Los logs: `sudo journalctl -u readyapi -f`
2. Estado de Nginx: `sudo systemctl status nginx`
3. Estado de la app: `sudo systemctl status readyapi`
4. Permisos de archivos: `ls -la /var/www/readyapi`

---

**¿Preguntas?** Revisa la documentación completa en [DEPLOYMENT_READYAPI.md](./deploy/DEPLOYMENT_READYAPI.md)
