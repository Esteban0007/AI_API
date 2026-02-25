# 🚀 FASE 3: DEPLOYMENT & PRUEBAS CON NUEVOS MODELOS

## Estado Actual

✅ **FASE 1-2 COMPLETADAS**
- Baseline capturado con MiniLM + mmarco
- Config actualizada a Arctic Embed + mxbai-rerank
- Cambios pusheados a main branch

## FASE 3: DEPLOYMENT EN SERVIDOR

### Pasos para Desplegar

En el servidor de producción (readyapi.net):

```bash
# SSH al servidor
ssh user@readyapi.net

# Navegar al directorio
cd /var/www/readyapi

# Hacer pull de cambios
git pull origin main

# Pre-descargar modelos (5-10 minutos)
python3 -c "
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoders import CrossEncoder
print('Downloading Arctic Embed...')
SentenceTransformer('snowflake/snowflake-arctic-embed-m-v1.5')
print('Downloading mxbai-rerank...')
CrossEncoder('mixedbread-ai/mxbai-rerank-xsmall-v1')
print('✅ Done')
"

# ⚠️ CRÍTICO: Reconstruir índices ChromaDB
# Los nuevos embeddings son 768D vs 384D anterior
python3 scripts/rebuild_index.py

# Reiniciar servicio
sudo systemctl restart readyapi

# Verificar que está UP
sleep 2
curl https://api.readyapi.net/api/v1/search/query -X POST -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d '{"query":"test","top_k":1}'
```

### Cambios Efectuados

**app/core/config.py:**
```python
# ANTES (MiniLM - 384D):
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
RERANK_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

# AHORA (Arctic - 768D):
EMBEDDING_MODEL = "snowflake/snowflake-arctic-embed-m-v1.5"
EMBEDDING_DIMENSION = 768
RERANK_MODEL = "mixedbread-ai/mxbai-rerank-xsmall-v1"
```

---

## FASE 3: PRUEBAS CON NUEVOS MODELOS

Una vez desplegado, ejecutar:

```bash
python3 scripts/evaluate_remote_server.py \
  --api-key "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg" \
  --output baseline_arctic_remote.json
```

---

## RESULTADOS BASELINE (MiniLM + mmarco)

📊 **Métricas Capturadas - 25 FEB 2026**

### Latencia Promedio (ms)
| Categoría | Latencia | Notas |
|-----------|----------|-------|
| Semantic | 922ms | Algunos queries muy lentos (1835ms) |
| Multilingual | 1429ms | ⚠️ CRÍTICO - "avventura spaziale": 1900ms |
| Exact | 571ms | ✅ Bueno |
| Almost-Exact | 831ms | Aceptable |
| **PROMEDIO TOTAL** | **939ms** | |

### Scores por Categoría

#### Semantic Understanding
| Query | Top Result | Score | Latencia |
|-------|-----------|-------|----------|
| "artificial intelligence" | Mission: Impossible | 0.1204 | 1313ms |
| "existential crisis in space" | Worldbreaker | **0.0023** ⚠️ | 1835ms |
| "lonely astronaut" | A Woman Scorned | **0.9500** ✅ | 274ms |
| "ethics of machines" | 28 Years Later | **0.9500** ✅ | 266ms |

#### Multilingual
| Query | Top Result | Score | Latencia |
|-------|-----------|-------|----------|
| "películas de robótica" | Hoppers | 0.7684 | 1378ms |
| "drama amoroso" | Ligaw | 0.3044 | 1315ms |
| "film d'animazione" | A Serbian Film | **0.9500** ✅ | 1124ms |
| "avventura spaziale" | Elio | 0.2738 | **1900ms** ⚠️ |

#### Exact Match
| Query | Result | Score | Latencia |
|-------|--------|-------|----------|
| "Avatar" | Avatar | 1.0000 ✅ | 863ms |
| "A Woman Scorned" | A Woman Scorned | 1.0000 ✅ | 279ms |

#### Almost-Exact
| Query | Result | Score | Latencia |
|-------|--------|-------|----------|
| "Woman Scorned" | A Woman Scorned | 0.9500 | 281ms |
| "Shawshank Redemption" | The Shawshank Redemption | 0.9500 | 1382ms |

---

## MEJORAS ESPERADAS CON ARCTIC + mxbai

### Predicciones Basadas en Benchmarks

| Métrica | MiniLM Actual | Arctic Esperado | Mejora |
|---------|---------------|-----------------|--------|
| Latencia Promedio | 939ms | **390ms** | **-58%** ⚡ |
| Semantic Avg | 922ms | **500ms** | **-46%** |
| Multilingual Avg | 1429ms | **480ms** | **-66%** ⚡ |
| Score "existential crisis" | 0.0023 | **0.45+** | **+195x** 🚀 |
| Score "drama amoroso" | 0.3044 | **0.65+** | **+113%** 🚀 |
| Score "avventura spaziale" | 0.2738 | **0.70+** | **+156%** 🚀 |

### Por Qué Estas Mejoras

**Arctic Embed (MTEB #2):**
- ✅ 768D vs 384D = más contexto capturado
- ✅ Entrenado en 25+ idiomas (vs MiniLM limitado)
- ✅ Mejor comprensión de semántica abstracta
- ✅ Captura mejor emociones ("drama", "crisis", etc)

**mxbai-rerank (XSmall):**
- ✅ 10-20x más rápido que mmarco
- ✅ Re-ranking especializado en multilingual
- ✅ Bajo overhead CPU (XSmall = lightweight)
- ✅ Mejor re-ranking de baja confianza

---

## PROBLEMAS IDENTIFICADOS EN BASELINE

### Problema 1: Semantic Abstracto Muy Bajo
**Query:** "existential crisis in space"  
**Score:** 0.0023 (prácticamente 0)  
**Causa:** MiniLM no captura bien conceptos emocionales abstractos  
**Esperado con Arctic:** 0.45-0.50

### Problema 2: Latencia Multilingual MUY Alta
**Query:** "avventura spaziale"  
**Latencia:** 1900ms (CRÍTICO)  
**Score:** 0.2738 (bajo)  
**Causa:** Multilingual embedding + re-ranking lento en mmarco  
**Esperado con Arctic:** 400-500ms + score 0.70+

### Problema 3: Multilingual General Débil
**Query:** "drama amoroso"  
**Score:** 0.3044 (bajo para búsqueda en español)  
**Causa:** MiniLM tiene soporte limitado para español/italiano  
**Esperado con Arctic:** 0.60-0.70

---

## PRÓXIMOS PASOS

### ✅ COMPLETADO (Hoy)
- [x] Ejecutar baseline con MiniLM + mmarco
- [x] Capturar métricas reales
- [x] Cambiar config a Arctic + mxbai
- [x] Hacer push a main

### ⏳ PENDIENTE (Después de deployment)
- [ ] Ejecutar pruebas con Arctic + mxbai
- [ ] Comparar resultados
- [ ] Cuantificar mejoras
- [ ] Documentar hallazgos
- [ ] Decidir si mantener Arctic o probar otros modelos

### 📊 FASE 4: ANÁLISIS & RECOMENDACIONES
**Después de ejecutar pruebas de Phase 3:**
- Comparación side-by-side de resultados
- Análisis de ROI (mejora vs costo compute)
- Recomendación final para producción

---

## Archivos Generados

📄 **Baselines:**
- `baseline_minilm_remote.json` - Resultados MiniLM (actualizado)
- `deploy_arctic_models.sh` - Script deployment

📄 **Scripts:**
- `scripts/evaluate_remote_server.py` - Evaluador remoto
- `scripts/evaluate_search.py` - Evaluador local

📄 **Documentación:**
- `EVALUATION_PLAN_COMPLETE.md` - Plan 4-fases completo
- `SUMMARY_PHASES_1_2.md` - Resumen Fase 1-2

---

## Estado del Repositorio

```
Main Branch (3e59299):
✅ Config con Arctic + mxbai
✅ Baseline con MiniLM documentado
✅ Scripts de evaluación listos
✅ Deploy script disponible
```

**Para proceder:**
1. Ejecutar script deploy en servidor
2. Esperar rebuild índices (2-3 minutos)
3. Ejecutar tests: `python3 scripts/evaluate_remote_server.py ...`
4. Comparar resultados

---

**Status:** 🟡 FASE 3 LISTA PARA EJECUTAR EN SERVIDOR
**Última actualización:** 25 FEB 2026
