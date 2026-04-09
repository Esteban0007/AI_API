# Implementación: GDPR Consent Tracking

## 📋 Resumen de Cambios

Has implementado un sistema completo de cumplimiento GDPR que registra cada aceptación de la Política de Privacidad con prueba técnica de consentimiento.

## 🔧 Cambios Realizados

### 1. **Modelo de Base de Datos**

📄 [`app/models/user.py`](app/models/user.py#L130)

- Nueva tabla `ConsentRecord` para almacenar registros de consentimiento
- Campos: `consent_status`, `consent_timestamp`, `consent_ip`, `privacy_version`, `consent_method`, `user_agent`

### 2. **Base de Datos SQLite**

📄 [`app/db/users.py`](app/db/users.py#L27)

- Tabla `consent_records` creada automáticamente en `init_db()`
- Funciones: `save_consent_record()`, `get_consent_records()`

### 3. **API Backend**

📄 [`app/api/web.py`](app/api/web.py#L165)

- Endpoint `POST /api/consent` para guardar consentimientos
- Captura automática de IP y User-Agent del request
- Retorna timestamp UTC del consentimiento

### 4. **Formulario de Registro (Frontend)**

📄 [`app/templates/register.html`](app/templates/register.html)

- JavaScript llama a `/api/consent` cuando el usuario hace submit
- Envía email, privacy_version (v1.0), y consent_method
- La API captura IP y User-Agent automáticamente

### 5. **Documentación de Cumplimiento**

📄 [`GDPR_COMPLIANCE.md`](GDPR_COMPLIANCE.md)

- Guía completa del sistema de consentimiento
- Esquema de base de datos
- Comandos SQL para auditoría
- Referencias regulatorias (GDPR, ePrivacy, CCPA)

### 6. **Script de Auditoría**

📄 [`scripts/view_consent_records.py`](scripts/view_consent_records.py)

- Visualizar todos los consentimientos registrados
- Ver consentimientos por usuario específico
- Estadísticas de consentimiento

---

## 📊 Datos Guardados por Consentimiento

```
Cuando el usuario marca el checkbox y envía el formulario:

✅ consent_status     → true (consentimiento aceptado)
⏰ consent_timestamp  → 2026-04-09 10:45:22 UTC (CUANDO exactamente)
🌐 consent_ip         → 85.54.XX.XXX (QUIÉN - IP del usuario)
📄 privacy_version    → v1.0 (QUÉ versión de la política)
📋 consent_method     → Web Form (CÓMO - forma de aceptación)
📧 user_email         → user@example.com (Email del usuario)
🔍 user_agent         → Mozilla/5.0... (Dispositivo/navegador)
```

---

## 🚀 Cómo Funciona en Producción

### Flujo durante el Registro:

1. **Usuario llena formulario**
   - Email, password, confirmación
2. **Usuario marca checkbox**
   - "I have read and agree to..." ✓
3. **Usuario envía formulario**
   - JavaScript captura email
   - Llamada POST a `/api/consent` con:
     ```json
     {
       "email": "user@example.com",
       "privacy_version": "v1.0",
       "consent_method": "Web Form"
     }
     ```
4. **Backend guarda consentimiento**
   - IP: `request.client.host` (automático)
   - User-Agent: header del navegador (automático)
   - Timestamp: UTC actual
   - Base de datos: INSERT en `consent_records`
5. **Registro continúa normalmente**
   - Usuario recibe email de confirmación
   - Consentimiento y registro están vinculados

---

## 🔍 Verificar Consentimientos Guardados

### Opción 1: Script de Python

```bash
# Ver todos los consentimientos
python scripts/view_consent_records.py

# Ver consentimientos de usuario específico
python scripts/view_consent_records.py user@example.com
```

### Opción 2: SQLite directo

```bash
sqlite3 data/users.db

# Ver todos los registros
SELECT * FROM consent_records ORDER BY consent_timestamp DESC;

# Ver consentimientos por usuario
SELECT * FROM consent_records
WHERE user_email = 'user@example.com'
ORDER BY consent_timestamp DESC;

# Ver últimas 24 horas
SELECT * FROM consent_records
WHERE consent_timestamp > datetime('now', '-1 day')
ORDER BY consent_timestamp DESC;
```

### Opción 3: Frontend (en navegador)

- Abrir Developer Tools (F12)
- Network tab
- Buscar requests a `/api/consent`
- Ver respuesta: `timestamp` del consentimiento registrado

---

## 📋 Cumplimiento GDPR

| Requisito                    | Status | Evidencia                           |
| ---------------------------- | ------ | ----------------------------------- |
| **Consentimiento Explícito** | ✅     | Checkbox + API call                 |
| **Lawful Basis**             | ✅     | Consentimiento explícito registrado |
| **Prueba de Consentimiento** | ✅     | Timestamp + IP + consent_status     |
| **Versión de Política**      | ✅     | privacy_version guardado            |
| **Derecho al Acceso**        | ✅     | Script view_consent_records.py      |
| **Auditoría Completa**       | ✅     | Tabla consent_records con metadata  |
| **Timestamp Preciso**        | ✅     | UTC con precisión de segundos       |
| **Origen Técnico**           | ✅     | IP address capturada                |

---

## 🔐 Datos de Auditoría

Cada registro incluye:

- **Legal**: Prueba de consentimiento (timestamp + IP + status)
- **Trazabilidad**: Email + policy version + método
- **Técnico**: User-Agent + IP para análisis de fraude
- **Temporal**: Cuándo exactamente ocurrió (GDPR Art. 7)

---

## 📝 Actualizando la Política de Privacidad

Cuando cambies tu Privacy Policy en el futuro:

1. Editar [`app/templates/privacy_policy.html`](app/templates/privacy_policy.html)
2. En el formulario, cambiar `privacy_version` de `v1.0` → `v1.1`
3. Usuarios nuevos aceptan `v1.1`, historial muestra quién aceptó cuál versión

```sql
-- Ver qué versión aceptó cada usuario
SELECT user_email, privacy_version, consent_timestamp
FROM consent_records
WHERE consent_status = 1
ORDER BY consent_timestamp DESC;
```

---

## 🛠️ Testing

Prueba el sistema en desarrollo:

```bash
# 1. Iniciar servidor
python -m uvicorn app.main:app --reload

# 2. Ir a http://localhost:8000/register

# 3. Llenar formulario y enviar
# - Verificar que consent_records tenga el nuevo registro
python scripts/view_consent_records.py

# 4. Ver en DevTools Network:
# - POST /api/consent con respuesta exitosa
```

---

## 📚 Referencias

- [`GDPR_COMPLIANCE.md`](GDPR_COMPLIANCE.md) - Documentación completa
- [`app/db/users.py`](app/db/users.py) - Funciones de consentimiento
- [`app/api/web.py`](app/api/web.py) - Endpoint de API
- [`app/templates/register.html`](app/templates/register.html) - Frontend

---

## ✅ Próximos Pasos (Opcionales)

- [ ] Endpoint para descargar consentimientos (Data Subject Access Request)
- [ ] Endpoint para revocar consentimiento (Right to Withdrawal)
- [ ] Email de confirmación de consentimiento
- [ ] Dashboard de admin para ver auditoría
- [ ] Exportar consentimientos a PDF para archivos legales
