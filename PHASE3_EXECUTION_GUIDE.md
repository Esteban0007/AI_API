# 🚀 PHASE 3: DEPLOYMENT & EXECUTION GUIDE

## Estado Actual ✅

- Baseline capturado: ✅ `baseline_minilm_remote.json`
- Config actualizada: ✅ App/core/config.py (Arctic + mxbai)
- Código pusheado: ✅ main branch
- Scripts listos: ✅ evaluate_remote_server.py, compare_baselines.py

**Falta:** Hacer deployment en servidor y re-ejecutar pruebas

---

## PASO 1: Hacer SSH al Servidor

```bash
ssh user@readyapi.net
# O si usas GitHub Actions/CI/CD, asegúrate que esté configurado
```

---

## PASO 2: Actualizar Código

```bash
cd /var/www/readyapi

# Hacer pull de cambios
git pull origin main

# Verificar que config.py tiene los nuevos modelos
grep -A2 "EMBEDDING_MODEL" app/core/config.py
# Debe mostrar: snowflake/snowflake-arctic-embed-m-v1.5
```

---

## PASO 3: Pre-Descargar Modelos (IMPORTANTE)

Los modelos se descargarán automáticamente en `~/.cache/huggingface/`

```bash
# Opción A: Descargar en background
python3 << 'EOF'
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoders import CrossEncoder

print("Downloading Arctic Embed (768D)...")
SentenceTransformer('snowflake/snowflake-arctic-embed-m-v1.5')
print("✅ Arctic Embed downloaded")

print("Downloading mxbai-rerank (XSmall)...")
CrossEncoder('mixedbread-ai/mxbai-rerank-xsmall-v1')
print("✅ mxbai-rerank downloaded")
EOF

# Opción B: En un screen/tmux para que siga si pierdes conexión
screen -S model_download
python3 << 'EOF'
# ... mismo código ...
EOF
# Ctrl+A, D para detach
```

**Tiempo estimado:** 5-10 minutos (depende del ancho de banda)

---

## PASO 4: ⚠️ CRÍTICO - Reconstruir Índices ChromaDB

**POR QUÉ:** Los embeddings nuevos son 768D en lugar de 384D. Los índices antiguos no son compatibles.

**TIEMPO:** 2-3 minutos (se reconstruye toda la DB)

```bash
# Opción A: Script automatizado (recomendado)
python3 scripts/rebuild_index.py

# Opción B: Manual (si necesitas ver más detalles)
python3 << 'EOF'
from engine.store import VectorStore
import shutil
from pathlib import Path

# Eliminar viejo índice
chroma_dir = Path("./data/chroma_db")
if chroma_dir.exists():
    shutil.rmtree(chroma_dir)
    print("Removed old indices")

# Crear store nuevo (se regenerará con 768D)
store = VectorStore(
    persist_dir="./data/chroma_db",
    collection_name="documents"
)

# Cargar documentos nuevamente
import json
docs = json.loads(Path("data/movies_dataset.json").read_text())["documents"]
success, failed = store.add_documents_batch(docs)
print(f"Reindexed: {success} documents, {failed} failed")
EOF
```

---

## PASO 5: Reiniciar Servicio

```bash
# Reiniciar
sudo systemctl restart readyapi

# Esperar 2-3 segundos
sleep 3

# Verificar que está up
systemctl status readyapi

# O hacer un test rápido
curl -X POST https://api.readyapi.net/api/v1/search/query \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","top_k":1}' | head -5
```

**Output esperado:** JSON con resultados (sin errores)

---

## PASO 6: Ejecutar Pruebas de Verificación (en máquina local)

Una vez que el servidor esté up con Arctic:

```bash
# Desde tu máquina local (no en el servidor)
cd /Users/estebanbardolet/Desktop/API_IA

# Ejecutar pruebas contra servidor actualizado
python3 scripts/evaluate_remote_server.py \
  --api-key "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg" \
  --output baseline_arctic_remote.json
```

**Esto generará:** `baseline_arctic_remote.json` con los resultados reales de Arctic

---

## PASO 7: Comparar Resultados

```bash
# Generar reporte comparativo
python3 scripts/compare_baselines.py \
  --minilm baseline_minilm_remote.json \
  --arctic baseline_arctic_remote.json \
  --output COMPARISON_REPORT.md

# Ver reporte
cat COMPARISON_REPORT.md
```

---

## VERIFICACIONES

### Verificación 1: ¿Latencia mejoró?

```bash
# Buscar en output
grep "avg_latency_ms" baseline_arctic_remote.json

# Esperado:
# "semantic": 400-500ms (vs 922ms antes)
# "multilingual": 450-600ms (vs 1429ms antes)
```

### Verificación 2: ¿Scores mejoraron en queries problemáticas?

```bash
# Buscar "existential crisis" en output
grep -A5 "existential crisis" baseline_arctic_remote.json

# Esperado:
# Score debe ser > 0.40 (vs 0.0023 antes)
```

### Verificación 3: ¿Multilingual mejoró?

```bash
# Buscar "avventura spaziale"
grep -A5 "avventura spaziale" baseline_arctic_remote.json

# Esperado:
# Latencia: < 700ms (vs 1900ms antes)
# Score: > 0.60 (vs 0.2738 antes)
```

---

## ROLLBACK (si algo falla)

Si necesitas volver a MiniLM rápidamente:

```bash
# En servidor
cd /var/www/readyapi

# Revertir config.py a MiniLM
git checkout HEAD~1 -- app/core/config.py

# Reconstruir índices de nuevo
python3 scripts/rebuild_index.py

# Reiniciar
sudo systemctl restart readyapi
```

---

## TIMELINE ESTIMADO

| Tarea                 | Tiempo        |
| --------------------- | ------------- |
| SSH + git pull        | 1 min         |
| Pre-descargar modelos | 5-10 min      |
| Reconstruir índices   | 2-3 min       |
| Reiniciar servicio    | 1 min         |
| Pruebas verificación  | 2-3 min       |
| Generar comparativa   | 1 min         |
| **TOTAL**             | **12-20 min** |

---

## CHECKLIST

- [ ] SSH a servidor
- [ ] Git pull de main
- [ ] Config tiene snowflake-arctic-embed-m-v1.5
- [ ] Pre-descargar modelos completado
- [ ] ChromaDB reconstruido (rebuild_index.py ejecutado)
- [ ] Servicio reiniciado (systemctl restart readyapi)
- [ ] Servidor responde a requests (curl test)
- [ ] Pruebas remotas ejecutadas (evaluate_remote_server.py)
- [ ] Reporte comparativo generado (compare_baselines.py)
- [ ] Mejoras verificadas vs predicciones

---

## TROUBLESHOOTING

### Problema: "ConnectionRefusedError" en pruebas

**Causa:** Servidor aún está iniciando o el deployment falló  
**Solución:** Esperar 5 segundos, verificar `systemctl status readyapi`

### Problema: "ImportError" al pre-descargar modelos

**Causa:** Dependencias faltantes  
**Solución:** `pip install sentence-transformers torch`

### Problema: ChromaDB rebuild tarda demasiado

**Causa:** Servidor lento o disco lleno  
**Solución:** Revisar `df -h` y `free -h`

### Problema: Scores no mejoraron

**Causa:** Config aún tiene MiniLM  
**Solución:** Verificar `git status`, hacer `git pull` de nuevo

---

## ARCHIVO IMPORTANTE

**MANTENER:** `baseline_minilm_remote.json`

- Este es nuestro baseline, no eliminar
- Necesario para comparación final

---

## DESPUÉS DE PHASE 3

1. ✅ Resultados reales con Arctic
2. ✅ Comparativa automática generada
3. ✅ Decisión: ¿mantener o cambiar?
4. → **PHASE 4: Análisis & Recomendaciones Finales**

---

**Documento:** PHASE3_EXECUTION_GUIDE.md  
**Versión:** 1.0  
**Status:** Ready to Execute  
**Última actualización:** 2026-02-25

IMPORTANTE: ⚠️ Esta es una guía para PHASE 3. Los cambios están listos en main branch.
Ejecutar cuando esté listo para desplegar en producción.
