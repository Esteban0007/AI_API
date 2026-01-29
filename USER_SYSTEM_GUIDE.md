# 🚀 Sistema de Usuarios y API Keys - Guía Completa

Sistema escalable de autenticación y facturación listo para integrar con **Stripe** u otros procesadores de pago.

---

## 📊 Arquitectura del Sistema

```
Usuario
  ↓
Registra cuenta → Selecciona Plan (Free/Pro/Enterprise)
  ↓
Recibe API Key automática
  ↓
Usa API Key en requests → Sistema valida + verifica límites
  ↓
Si excede límites → Debe actualizar plan
  ↓
Pago vía Stripe → Webhook actualiza plan automáticamente
```

---

## 🗄️ Modelos de Base de Datos

### 1. **Plan** - Planes de suscripción

```python
- free: $0/mes - 100 búsquedas/día
- pro: $29/mes - 10,000 búsquedas/día
- enterprise: $299/mes - Ilimitado
```

### 2. **User** - Usuarios/Organizaciones

```python
- email, nombre, empresa
- plan_id (FK a Plan)
- stripe_customer_id, stripe_subscription_id
- subscription_status (active/canceled/past_due)
```

### 3. **APIKey** - Claves de autenticación

```python
- key (formato: rapi_xxx...)
- user_id (FK a User)
- nombre, is_active
- last_used_at, total_requests
```

### 4. **Usage** - Tracking de uso diario

```python
- user_id, date
- searches_count, documents_indexed
- billable_searches (para facturación)
```

### 5. **PaymentHistory** - Historial de pagos

```python
- stripe_payment_intent_id
- amount, status, paid_at
```

---

## 🎯 Flujo de Usuario (Super Simple)

### Para el Admin (tú):

```bash
# 1. Inicializar base de datos (solo una vez)
python scripts/init_db.py

# 2. Crear usuario con plan FREE
python scripts/create_user.py \
  --email cliente@empresa.com \
  --name "Juan Pérez" \
  --company "Empresa SA" \
  --plan free

# Output:
# ✅ USER CREATED SUCCESSFULLY
# 📧 Email: cliente@empresa.com
# 🔑 API KEY: rapi_xk82jd9kasd7823hd9812h3k2j
```

### Para el Usuario (cliente):

```python
import requests

# Usar la API key
response = requests.post(
    "https://readyapi.net/api/v1/search/query",
    headers={"X-API-Key": "rapi_xk82jd9kasd7823hd9812h3k2j"},
    json={"query": "machine learning", "top_k": 5}
)

# Ver su uso
usage = requests.get(
    "https://readyapi.net/api/v1/users/usage",
    headers={"X-API-Key": "rapi_xk82jd9kasd7823hd9812h3k2j"}
)
# {
#   "searches_today": 45,
#   "daily_limit": 100,
#   "remaining_today": 55
# }
```

---

## 🔐 Endpoints Disponibles

### Autenticación (requieren X-API-Key)

#### `GET /api/v1/users/me`

Información del usuario actual

```json
{
  "id": 1,
  "email": "user@example.com",
  "plan_name": "pro",
  "is_active": true
}
```

#### `GET /api/v1/users/usage`

Uso y límites actuales

```json
{
  "searches_today": 45,
  "searches_this_month": 1200,
  "daily_limit": 10000,
  "remaining_today": 9955
}
```

#### `GET /api/v1/users/api-keys`

Lista de API keys del usuario

```json
[
  {
    "id": 1,
    "name": "Production App",
    "key_prefix": "rapi_xk82jd...",
    "is_active": true,
    "total_requests": 5432
  }
]
```

#### `POST /api/v1/users/api-keys`

Crear nueva API key

```json
{
  "name": "Mobile App"
}
// Response:
{
  "key": "rapi_new_key_here",  // ⚠️ Solo se muestra una vez!
  "message": "Save it securely - it won't be shown again!"
}
```

#### `DELETE /api/v1/users/api-keys/{id}`

Desactivar una API key

### Facturación

#### `GET /api/v1/billing/plans` (público)

Lista de planes disponibles

#### `GET /api/v1/billing/subscription`

Suscripción actual del usuario

#### `POST /api/v1/billing/webhook/stripe`

Webhook para eventos de Stripe

---

## 💳 Integración con Stripe (Preparada)

### 1. Configurar Stripe

```bash
# En .env
STRIPE_SECRET_KEY=sk_live_xxx...
STRIPE_WEBHOOK_SECRET=whsec_xxx...
```

### 2. Crear Precios en Stripe Dashboard

```
Free Plan: $0/mes (gratis)
Pro Plan: $29/mes → stripe_price_id_monthly
Enterprise: $299/mes → stripe_price_id_monthly
```

### 3. Configurar Webhook en Stripe

```
URL: https://readyapi.net/api/v1/billing/webhook/stripe

Eventos a escuchar:
- checkout.session.completed
- invoice.payment_succeeded
- invoice.payment_failed
- customer.subscription.updated
- customer.subscription.deleted
```

### 4. Crear Link de Pago

```python
# Cuando el usuario quiere actualizar a Pro
import stripe

checkout_session = stripe.checkout.Session.create(
    customer=user.stripe_customer_id,  # Ya lo tienes en BD
    line_items=[{
        'price': 'price_xxx',  # Pro plan price ID
        'quantity': 1,
    }],
    mode='subscription',
    success_url='https://readyapi.net/success',
    cancel_url='https://readyapi.net/cancel',
)

# Redirigir usuario a: checkout_session.url
```

### 5. El Webhook Hace el Resto

Cuando el pago se completa:

1. Stripe envía webhook a tu API
2. `handle_payment_succeeded()` se ejecuta
3. Actualiza `user.plan_id` a Pro automáticamente
4. Usuario ya tiene más límites ✅

---

## 🛠️ Scripts de Administración

### `scripts/init_db.py`

Inicializa base de datos y crea planes default

```bash
python scripts/init_db.py
```

### `scripts/create_user.py`

Crea nuevo usuario con API key

```bash
python scripts/create_user.py \
  --email user@example.com \
  --name "John Doe" \
  --company "Acme Inc" \
  --plan pro
```

### `scripts/list_users.py`

Lista todos los usuarios y sus API keys

```bash
python scripts/list_users.py
```

---

## 📈 Sistema de Límites (Rate Limiting)

El sistema valida automáticamente:

```python
@router.post("/search/query")
async def search(
    query: SearchQuery,
    user_context: dict = Depends(check_rate_limit)  # ← Valida límites
):
    # Si excedió límites, lanza HTTP 429 Too Many Requests
    # Si está ok, continúa normalmente
```

**Límites por plan:**

| Plan       | Búsquedas/día | Búsquedas/mes | Documentos | API Keys  |
| ---------- | ------------- | ------------- | ---------- | --------- |
| Free       | 100           | 1,000         | 10,000     | 1         |
| Pro        | 10,000        | 200,000       | 1,000,000  | 10        |
| Enterprise | 100,000       | Ilimitado     | Ilimitado  | Ilimitado |

---

## 🔄 Migración de SQLite a PostgreSQL (Futuro)

Cuando crezcas:

```python
# 1. Instalar PostgreSQL
apt install postgresql

# 2. Crear base de datos
createdb readyapi_db

# 3. Cambiar en .env
DATABASE_URL=postgresql://user:pass@localhost/readyapi_db

# 4. Reiniciar - las tablas se crean automáticamente
python scripts/init_db.py
```

El código ya está preparado para ambos 👍

---

## ✅ Ventajas de esta Arquitectura

1. **Para el usuario:**
   - ✅ Un solo comando genera su API key
   - ✅ No necesita registrarse en web (por ahora)
   - ✅ Recibe key por email/mensaje
   - ✅ La usa inmediatamente

2. **Para ti (admin):**
   - ✅ Control total de usuarios
   - ✅ Tracking de uso en tiempo real
   - ✅ Fácil actualizar planes
   - ✅ Listo para pagos automáticos

3. **Escalabilidad:**
   - ✅ Migración fácil a PostgreSQL
   - ✅ Webhook de Stripe ya implementado
   - ✅ Sistema de planes flexible
   - ✅ Rate limiting por usuario

---

## 🚦 Próximos Pasos Opcionales

1. **Dashboard Web** (Frontend):
   - Registro de usuarios
   - Login con email/password
   - Ver estadísticas de uso
   - Actualizar plan (Stripe Checkout)

2. **Email Notifications**:
   - Bienvenida con API key
   - Alertas de límite alcanzado
   - Recordatorios de pago

3. **Analytics**:
   - Dashboard de métricas
   - Usuarios activos
   - Revenue tracking

---

## 📚 Documentación API Automática

Una vez iniciado el servidor:

- **Swagger UI:** https://readyapi.net/api/docs
- **ReDoc:** https://readyapi.net/api/redoc

Muestra todos los endpoints con ejemplos de uso.

---

## 🎉 ¡Listo para Usar!

```bash
# 1. Inicializar
python scripts/init_db.py

# 2. Crear primer usuario
python scripts/create_user.py --email admin@readyapi.net --name "Admin"

# 3. Arrancar servidor
python scripts/run_server.py

# 4. Probar API
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "X-API-Key: rapi_xxx"
```

**El sistema es:**

- ✅ Simple para usuarios
- ✅ Escalable para crecimiento
- ✅ Listo para pagos
- ✅ Fácil de mantener
