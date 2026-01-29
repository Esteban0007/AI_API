# 🚀 Quick Start - Sistema de Usuarios

## Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Inicializar base de datos
python scripts/init_db.py

# 3. Crear tu primer usuario
python scripts/create_user.py \
  --email admin@readyapi.net \
  --name "Admin ReadyAPI" \
  --plan free

# Guarda la API key que te muestra! (rapi_xxx...)

# 4. Iniciar servidor
python scripts/run_server.py
```

## Uso Básico

```bash
# Obtener info del usuario
curl http://localhost:8000/api/v1/users/me \
  -H "X-API-Key: rapi_TU_KEY_AQUI"

# Ver uso y límites
curl http://localhost:8000/api/v1/users/usage \
  -H "X-API-Key: rapi_TU_KEY_AQUI"

# Hacer búsqueda (con rate limiting)
curl -X POST http://localhost:8000/api/v1/search/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rapi_TU_KEY_AQUI" \
  -d '{"query": "machine learning", "top_k": 5}'
```

## Gestión de Usuarios

```bash
# Listar todos los usuarios
python scripts/list_users.py

# Crear usuario PRO
python scripts/create_user.py \
  --email premium@empresa.com \
  --name "Cliente Premium" \
  --company "Empresa SA" \
  --plan pro
```

## Documentación Completa

- **Sistema de Usuarios:** [USER_SYSTEM_GUIDE.md](USER_SYSTEM_GUIDE.md)
- **Deployment HTTPS:** [deploy/DEPLOYMENT_READYAPI.md](deploy/DEPLOYMENT_READYAPI.md)
- **API Docs:** http://localhost:8000/api/docs

## 💳 Stripe (Opcional - Futuro)

Cuando quieras activar pagos:

1. Descomenta `stripe` en [requirements.txt](requirements.txt)
2. Configura `STRIPE_SECRET_KEY` y `STRIPE_WEBHOOK_SECRET` en `.env`
3. El webhook ya está listo en `/api/v1/billing/webhook/stripe`

Ver detalles en [USER_SYSTEM_GUIDE.md](USER_SYSTEM_GUIDE.md#-integración-con-stripe-preparada)
