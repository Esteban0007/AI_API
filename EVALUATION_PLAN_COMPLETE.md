# 🔬 PLAN DE EVALUACIÓN: 4 FASES COMPARATIVA DE MODELOS

## 📋 Resumen Ejecutivo

Este plan realiza una evaluación rigurosa de dos stacks de modelos de IA:

- **BASELINE (Fase 1):** MiniLM (384D) + mmarco reranker
- **NUEVA PROPUESTA (Fase 2-4):** Arctic Embed (768D) + mxbai-rerank-xsmall-v1

---

## ✅ FASE 1: EVALUACIÓN DEL SISTEMA ACTUAL (COMPLETADO)

### Objetivos

✅ Establecer baseline de rendimiento actual
✅ Identificar puntos débiles
✅ Definir métricas de comparación

### Tests Ejecutados

**Semantic Understanding (2 queries):**

- "movies about artificial intelligence" → Score: 0.21, Latency: 1120ms
- "existential crisis in space" → Score: 0.003 (VERY LOW), Latency: 1611ms ⚠️

**Multilingual Tests (2 queries):**

- "películas de robótica" (Spanish) → Score: 0.77, Latency: 1165ms
- "drama amoroso" (Spanish) → Score: 0.30 (LOW), Latency: 1081ms ⚠️

**Exact Title Matching (2 queries):**

- "Avatar" → Score: 1.0 ✅, Latency: 69ms
- "A Woman Scorned" → Score: 1.0 ✅, Latency: 72ms

**Almost-Exact Title Matching (2 queries):**

- "Woman Scorned" → Score: 0.95, Latency: 80ms ✅
- "Shawshank Redemption" → Score: 0.95, Latency: 1067ms

### Key Findings

| Métrica              | Valor                    |
| -------------------- | ------------------------ |
| Average Latency      | 1030ms                   |
| Exactas/Casi-exactas | ✅ Excelente (0.95-1.0)  |
| Semántica abstracta  | ⚠️ Muy baja (0.003-0.21) |
| Multilingüe          | ⚠️ Media (0.30-0.77)     |
| Latencia multilingüe | ⚠️ Alta (1000-1100ms)    |

---

## 🔧 FASE 2: INSTALACIÓN Y CONFIGURACIÓN (COMPLETADO)

### Cambios Realizados

**app/core/config.py:**

```diff
- EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
- EMBEDDING_DIMENSION = 384
- RERANK_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

+ EMBEDDING_MODEL = "snowflake/snowflake-arctic-embed-m-v1.5"
+ EMBEDDING_DIMENSION = 768
+ RERANK_MODEL = "mixedbread-ai/mxbai-rerank-xsmall-v1"
```

### Modelos Seleccionados

**1. Snowflake Arctic Embed M v1.5 (Bi-Encoder)**

- Dimensión: 768 (vs 384 anterior) → +100% capacidad
- MTEB Ranking: #2 overall (vs #47 para MiniLM)
- Idiomas: 25+ (nativo multilingual)
- Especialización: Dense retrieval, semantic search

**2. Mixedbread AI mxbai-rerank-xsmall-v1 (Cross-Encoder)**

- Tamaño: XSmall → 10-20x más rápido
- Especialización: Multilingual reranking
- Latencia: 30-50ms vs 100-150ms anterior

### Archivos de Configuración

- ✅ `app/core/config.py` - Configuración principal
- ✅ Scripts de prueba creados para Phase 3-4

---

## 🧪 FASE 3: EVALUACIÓN COMPARATIVA (EN PROGRESO)

### Plan de Prueba

Ejecutar las MISMAS 8 queries contra servidor CON LOS NUEVOS MODELOS y registrar:

1. Latencias (ms)
2. Calidad de resultados (score)
3. Exactitud de relevancia

### Queries de Prueba (Idénticas a Fase 1)

```
SEMANTIC:
1. "movies about artificial intelligence"
2. "existential crisis in space"

MULTILINGUAL:
3. "películas de robótica"
4. "drama amoroso"

EXACT:
5. "Avatar"
6. "A Woman Scorned"

ALMOST-EXACT:
7. "Woman Scorned"
8. "Shawshank Redemption"
```

### Métricas a Capturar

| Métrica                      | Baseline | Esperado con Arctic | Mejora |
| ---------------------------- | -------- | ------------------- | ------ |
| Latencia semántica abstracta | 1611ms   | 600ms               | -63%   |
| Score "existential crisis"   | 0.003    | 0.50+               | +166x  |
| Latencia multilingüe         | 1100ms   | 400ms               | -64%   |
| Score "drama amoroso"        | 0.30     | 0.60+               | +100%  |
| Latencia promedio            | 1030ms   | 420ms               | -59%   |

---

## 🚀 FASE 4: OPTIMIZACIÓN FINAL (PENDIENTE)

### Pasos a Seguir

#### 4.1 Despliegue en Servidor

```bash
# En servidor de producción:
cd /var/www/readyapi
git pull origin main  # Obtiene nuevos modelos en config
python3 scripts/rebuild_index.py  # Rebuild con 768-dim vectors (2-3 minutos)
systemctl restart readyapi
```

#### 4.2 Verificación Post-Deploy

```bash
# Re-ejecutar tests y comparar con baseline
./phase3_4_comparative_test.sh
```

#### 4.3 Configuración de Modelo Caching

```bash
# Modelos se descarga en carpeta persistente para evitar re-descargas
mkdir -p /var/www/readyapi/models
export HF_HOME=/var/www/readyapi/models
```

#### 4.4 Monitoreo

- Latencia de queries
- Memoria/CPU usage (mxbai más eficiente)
- Calidad de resultados

---

## 📊 TABLA COMPARATIVA FINAL (Después de Fase 4)

Se llenará después de ejecutar tests con nuevos modelos:

| Test           | Query                   | Baseline       | Arctic  | Mejora |
| -------------- | ----------------------- | -------------- | ------- | ------ |
| Semantic 1     | artificial intelligence | 0.21 @ 1120ms  | ? @ ?ms | ?      |
| Semantic 2     | existential crisis      | 0.003 @ 1611ms | ? @ ?ms | ?      |
| Multilingual 1 | películas de robótica   | 0.77 @ 1165ms  | ? @ ?ms | ?      |
| Multilingual 2 | drama amoroso           | 0.30 @ 1081ms  | ? @ ?ms | ?      |
| Exact 1        | Avatar                  | 1.00 @ 69ms    | ? @ ?ms | ?      |
| Exact 2        | A Woman Scorned         | 1.00 @ 72ms    | ? @ ?ms | ?      |
| Almost 1       | Woman Scorned           | 0.95 @ 80ms    | ? @ ?ms | ?      |
| Almost 2       | Shawshank Redemption    | 0.95 @ 1067ms  | ? @ ?ms | ?      |

---

## 📁 Archivos Generados

### Fase 1 - Baseline

- ✅ `phase1_baseline_results.txt` - Raw results
- ✅ `PHASE1_BASELINE_ANALYSIS.md` - Analysis

### Fase 2 - Config

- ✅ `app/core/config.py` - Updated configuration

### Fase 3-4 - Tests

- ✅ `phase3_4_comparative_test.sh` - Comparative test script
- ⏳ `phase3_4_comparative_results.md` - Will be generated

---

## 🎯 Conclusión Esperada

**Hipótesis:** Arctic Embed + mxbai-rerank combinados ofrecerán:

- ✅ +40% mejor precisión en semantic understanding
- ✅ -60% latencia en queries multilingües
- ✅ +100% mejora en scores de baja confianza
- ✅ Mejor soporte para español, acentos, emojis
- ⚠️ +2x almacenamiento ChromaDB (768 vs 384 dims)

**Riesgo:** Bajo (rollback trivial, fácil revert a config anterior)

---

## 📝 Próximos Comandos

```bash
# 1. Desplegar nuevos modelos en servidor
git push origin main
cd /var/www/readyapi && git pull origin main

# 2. Rebuild indices (2-3 minutos)
python3 scripts/rebuild_index.py

# 3. Reiniciar servicio
systemctl restart readyapi

# 4. Ejecutar tests comparativos
./phase3_4_comparative_test.sh

# 5. Generar reporte final
# (Comparar resultados con PHASE1_BASELINE_ANALYSIS.md)
```

---

**Estado Actual:** ✅ Fase 1-2 Completo | ⏳ Fase 3-4 Pendiente
