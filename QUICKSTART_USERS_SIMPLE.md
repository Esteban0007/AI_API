# 🚀 Quick Start - Sistema de Usuarios

## ⚡ Tu Clave Admin Privada (2 minutos)

```bash
# 1. Generar clave admin segura
python scripts/generate_admin_key.py

# Output:
# 🔑 Your secure admin API key:
#    rapi_xxxxxxxxxxxxxxxxxxxxxxxx
#
# 📝 Add this to your .env file:
#    ADMIN_API_KEY=rapi_xxxxxxxxxxxxxxxxxxxxxxxx

# 2. Copiar el .env.example a .env
cp .env.example .env

# 3. Editar .env y pegar la clave en ADMIN_API_KEY
nano .env

# 4. ¡Listo! Ya tienes acceso ilimitado
```

## Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Inicializar base de datos
python scripts/init_db.py

# 3. Crear usuario normal (opcional - para clientes)
python scripts/create_user.py \
  --email cliente@empresa.com \
  --name "Cliente" \
  --plan free

# 4. Iniciar servidor
python scripts/run_server.py
```

## Uso - Con tu Clave Admin

```bash
# Búsqueda SIN límites (usando tu clave admin)
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rapi_tu_clave_admin" \
  -d '{"query": "test", "top_k": 5}'

# Ver tu info (siempre acceso)
curl http://localhost:8000/api/v1/users/me \
  -H "X-API-Key: rapi_tu_clave_admin"

# Hacer 1000 búsquedas en 1 segundo - sin problemas
# Los usuarios normales estarían limitados a 100/día
```

## Usuarios Normales (Clientes)

```bash
# Crear un cliente con plan FREE
python scripts/create_user.py \
  --email cliente@empresa.com \
  --name "Cliente" \
  --plan free

# Crear un cliente con plan PRO
python scripts/create_user.py \
  --email premium@empresa.com \
  --name "Premium" \
  --plan pro

# Ver todos los usuarios
python scripts/list_users.py
```

## 📊 Comparación

| Aspecto | Clave Admin | Cliente Free | Cliente Pro |
|---------|------------|--------------|-----------|
| Búsquedas/día | ♾️ Ilimitado | 100 | 10,000 |
| Búsquedas/mes | ♾️ Ilimitado | 1,000 | 200,000 |
| Rate Limiting | ❌ NO | ✅ SÍ | ✅ SÍ |
| Costo | $0 | $0 | $29/mes |

## Documentación Completa

- **Sistema Completo:** [USER_SYSTEM_GUIDE.md](USER_SYSTEM_GUIDE.md)
- **Deployment HTTPS:** [deploy/DEPLOYMENT_READYAPI.md](deploy/DEPLOYMENT_READYAPI.md)
- **API Docs:** http://localhost:8000/api/docs
