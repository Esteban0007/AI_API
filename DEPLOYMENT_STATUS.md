# ⚠️ ESTADO ACTUAL: SERVIDOR NO DESPLEGADO

**Fecha de verificación:** 25 FEB 2026  
**Estado:** ❌ SERVIDOR AÚN CON MODELOS ANTIGUOS

---

## 📊 Verificación de Estado

### Prueba Ejecutada

```bash
python3 scripts/evaluate_remote_server.py --api-key "..." --output test_current_server.json
```

### Resultados de la Verificación

El servidor SIGUE CON LOS MODELOS ANTIGUOS (MiniLM + mmarco):

| Query                         | Latencia | Score  | Observación                  |
| ----------------------------- | -------- | ------ | ---------------------------- |
| "existential crisis in space" | 1846ms   | 0.0023 | ❌ IGUAL que baseline MiniLM |
| "avventura spaziale"          | 1950ms   | 0.2738 | ❌ IGUAL que baseline MiniLM |
| "Avatar"                      | 1916ms   | 1.0000 | ❌ MÁS LENTO (antes: 863ms)  |

**Conclusión:** El servidor NO ha hecho `git pull` automáticamente. Los cambios están en GitHub pero no desplegados.

---

## 🔧 QUÉ NECESITA HACERSE

### Opción 1: Deployment Manual en Servidor (RECOMENDADO)

**En la máquina del servidor (readyapi.net):**

```bash
cd /var/www/readyapi

# 1. Parar servicio
sudo systemctl stop readyapi

# 2. Actualizar código
git fetch origin main
git reset --hard origin/main

# 3. Descargar modelos (5-10 minutos en primer run)
python3 -c "
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoders import CrossEncoder
print('Descargando Arctic Embed...')
SentenceTransformer('snowflake/snowflake-arctic-embed-m-v1.5')
print('Descargando mxbai-rerank...')
CrossEncoder('mixedbread-ai/mxbai-rerank-xsmall-v1')
print('✅ Modelos descargados')
"

# 4. ⚠️ CRÍTICO: Reconstruir índices (2-3 minutos)
# Los nuevos embeddings son 768D vs 384D anterior
python3 scripts/rebuild_index.py

# 5. Reiniciar servicio
sudo systemctl start readyapi

# 6. Verificar
sleep 2
systemctl status readyapi
```

### Opción 2: Script Automático (Proporcionado)

Ejecutar el script preparado en el servidor:

```bash
chmod +x MANUAL_DEPLOYMENT.sh
./MANUAL_DEPLOYMENT.sh
```

### Opción 3: Usar SSH desde Local (Si tienes acceso)

```bash
# Desde tu máquina local:
ssh user@readyapi.net "cd /var/www/readyapi && bash <<'EOF'
sudo systemctl stop readyapi
git fetch origin main && git reset --hard origin/main
python3 -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('snowflake/snowflake-arctic-embed-m-v1.5')\"
python3 -c \"from sentence_transformers.cross_encoders import CrossEncoder; CrossEncoder('mixedbread-ai/mxbai-rerank-xsmall-v1')\"
python3 scripts/rebuild_index.py
sudo systemctl start readyapi
EOF
"
```

---

## ✅ VERIFICACIÓN POST-DEPLOYMENT

Una vez desplegado, verificar que funciona ejecutando:

```bash
# LOCAL MACHINE
cd /Users/estebanbardolet/Desktop/API_IA

# 1. Ejecutar pruebas con nuevos modelos
python3 scripts/evaluate_remote_server.py \
  --api-key "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg" \
  --output baseline_arctic_remote.json

# 2. Verificar mejoras esperadas:
# - "existential crisis in space": debe ser score > 0.4 (era 0.0023)
# - "avventura spaziale": debe ser < 600ms (era 1950ms)
# - Latencia promedio: debe bajar a ~400ms (era ~1400ms)

# 3. Comparar con baseline original
python3 scripts/compare_baselines.py \
  --minilm baseline_minilm_remote.json \
  --arctic baseline_arctic_remote.json \
  --output comparison_report.md
```

---

## 🎯 Checklist de Deployment

```
En el servidor (readyapi.net):
☐ Parar servicio: sudo systemctl stop readyapi
☐ Git pull: git fetch origin main && git reset --hard origin/main
☐ Descargar Arctic Embed (~500MB, 2-3 min)
☐ Descargar mxbai-rerank (~100MB, 1 min)
☐ Reconstruir índices: python3 scripts/rebuild_index.py (2-3 min)
☐ Iniciar servicio: sudo systemctl start readyapi
☐ Verificar status: systemctl is-active readyapi

En tu máquina local:
☐ Ejecutar pruebas con nuevos modelos
☐ Generar reporte de comparación
☐ Validar mejoras esperadas
```

---

## ⏱️ Timeline Estimado

| Paso             | Tiempo        | Notas                     |
| ---------------- | ------------- | ------------------------- |
| Git pull         | 1 min         |                           |
| Descargar Arctic | 3-5 min       | Primer run, luego cache   |
| Descargar mxbai  | 1 min         | Más pequeño               |
| Rebuild índices  | 2-3 min       | ⚠️ Sin servicio           |
| Restart servicio | 1 min         |                           |
| Pruebas locales  | 5 min         |                           |
| **TOTAL**        | **12-16 min** | Con servicio DOWN 5-6 min |

---

## 📋 Archivos Relevantes

- `MANUAL_DEPLOYMENT.sh` - Script completo de deployment
- `deploy_arctic_models.sh` - Versión alternativa más simple
- `PHASE3_EXECUTION_GUIDE.md` - Guía detallada Phase 3
- `PHASE3_DEPLOYMENT_STATUS.md` - Status y próximos pasos

---

## ⚡ Próximos Pasos

**INMEDIATO:**

1. ✋ Hacer deployment manual en servidor (opciones arriba)

**DESPUÉS DE DEPLOYMENT:** 2. ✅ Verificar que servidor responde 3. 🧪 Ejecutar pruebas con nuevos modelos 4. 📊 Generar reporte comparativo 5. 🎉 Documentar resultados finales

**STATUS ACTUAL:** Esperando deployment manual en servidor
