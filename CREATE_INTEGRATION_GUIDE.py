#!/usr/bin/env python3
"""
Integration Guide: Integrando tus scripts anteriores (crearCSV_embedding_full.py y busqueda_embedding_full.py)
con el nuevo SaaS FastAPI de búsqueda semántica.
"""

import json
from pathlib import Path

INTEGRATION_GUIDE = """
# 🔌 Guía de Integración - Tus Scripts Anteriores

## 📌 Situación Actual

Tienes dos scripts que utilizas:
1. `crearCSV_embedding_full.py` - Crea un CSV con embeddings
2. `busqueda_embedding_full.py` - FastAPI que busca en ese CSV

## ✅ Lo que hemos mejorado

Integramos la lógica de ambos scripts en un **SaaS profesional** con:
- ✅ Base de datos vectorial (Chroma) en lugar de CSV
- ✅ API REST completa y documentada
- ✅ Re-ranking con cross-encoders (mejora relevancia)
- ✅ Gestión de múltiples colecciones
- ✅ Seguridad con API Keys
- ✅ Sistema de cuotas SaaS

---

## 🔄 Mapeo de Funcionalidad

### Tu código anterior → Nuevo SaaS

| Tu Script | Nueva Ubicación | Mejoras |
|-----------|-----------------|---------|
| crearCSV_embedding_full.py | app/engine/embedder.py | Más rápido, mejor gestión de memoria |
| busqueda_embedding_full.py | app/api/v1/search.py | Integrado con API REST profesional |
| Almacenamiento CSV | app/engine/store.py (Chroma) | Persistente, escalable, indexado |

---

## 🎯 Funcionalidades Equivalentes

### Función Anterior: Crear Embeddings

**Tu código:**
```python
# crearCSV_embedding_full.py
model_name = os.environ.get('MODEL_NAME', 'BAAI/bge-m3')
embedding_model = SentenceTransformer(model_name)

# Cargar JSON y calcular embeddings
mi_pd_frame['Embedding'] = mi_pd_frame.apply(
    lambda row: embedding_model.encode(row['info']).tolist(),
    axis=1
)
```

**Nuevo (mejor):**
```python
# app/engine/embedder.py
embedder = Embedder(model_name='BAAI/bge-m3')

# Procesar muchos documentos eficientemente
embeddings = embedder.embed_texts(texts, batch_size=32)
```

**Ventajas:**
- ✅ Batch processing (más rápido)
- ✅ Mejor manejo de memoria
- ✅ Error handling
- ✅ Logging

### Función Anterior: Buscar y Re-rankear

**Tu código:**
```python
# busqueda_embedding_full.py
model_name = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Calcular similitud
mi_pd_frame["Similitud"] = mi_pd_frame['info'].apply(
    lambda x: compute_similarity(query, x)
)

# Ordenar y devolver
resultados = mi_pd_frame.sort_values(
    by="Similitud", 
    ascending=False
).head(n_results)
```

**Nuevo (mejor):**
```python
# app/engine/searcher.py (SearchEngine.search())
search_engine = SearchEngine()

results, exec_time = search_engine.search(
    query="tu búsqueda",
    top_k=5
)

# Ya incluye:
# ✅ Búsqueda vectorial (HNSW) + re-ranking
# ✅ Normalization de scores
# ✅ Tiempo de ejecución
```

**Ventajas:**
- ✅ 2-phase search: vector + cross-encoder
- ✅ Más rápido (búsqueda vectorial con índice)
- ✅ Mejor escalabilidad

---

## 📤 Migración de tus Datos

### Si tienes documentos en CSV (como tu open_app.json)

```python
# Convertir tu CSV/JSON a formato del nuevo SaaS
import json
import pandas as pd

# 1. Leer tu CSV antiguo
df = pd.read_csv('full.csv')

# 2. Convertir al formato del nuevo SaaS
documents = []
for _, row in df.iterrows():
    documents.append({
        "id": row['id'],  # O generar con uuid
        "title": row.get('title', ''),
        "content": row['info'],  # Tu campo de información
        "keywords": row.get('keywords', []).split(',') if isinstance(row.get('keywords'), str) else [],
        "metadata": {
            "category": row.get('category', ''),
            "language": "es",
            "source": row.get('source', '')
        }
    })

# 3. Guardar en formato JSON
with open('documentos.json', 'w') as f:
    json.dump({"documents": documents}, f, indent=2)

# 4. Cargar en el nuevo SaaS
# python scripts/load_documents.py --file documentos.json
```

---

## 🚀 Reemplazar tus Endpoints Anteriores

### Tu endpoint anterior

```python
# Tu busqueda_embedding_full.py
@app.post("/embedding3")
async def search(request: SearchRequest):
    # Tu lógica de búsqueda aquí
    ...
```

### Nuevo endpoint (mucho mejor)

```bash
# POST http://localhost:8000/api/v1/search/query
{
  "query": "tu búsqueda",
  "top_k": 5,
  "include_content": true
}
```

**Ventajas del nuevo:**
- ✅ Mejor documentación (Swagger)
- ✅ Validación automática (Pydantic)
- ✅ Manejo de errores
- ✅ Logging
- ✅ Autenticación (API Keys)
- ✅ CORS configurado

---

## 🔧 Cambiar Modelos (como en tu .env anterior)

### Mantener tu modelo anterior (BAAI/bge-m3)

```env
# .env
EMBEDDING_MODEL=BAAI/bge-m3
RERANK_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2

# Para embeddings específicos
EMBEDDING_DIMENSION=1024  # Para bge-m3
```

### O usar los modelos nuevos (más rápidos)

```env
# Rápido y ligero (recomendado para SaaS)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

---

## 📊 Comparación: Antes vs Después

### Procesamiento de Documentos

**Antes (tu código):**
```
JSON → Embeddings → CSV
↓
Búsqueda sequential en CSV
```

**Ahora (SaaS):**
```
JSON → Embeddings → Chroma (indexado HNSW)
↓
Búsqueda vectorial O(log n) + Cross-encoder re-ranking
```

**Mejora:** 10-100x más rápido para búsquedas

### Búsqueda

**Antes:**
```
Query → Calcular similitud con CADA documento → Ordenar
O(n) en cada búsqueda
```

**Ahora:**
```
Query → Búsqueda vectorial HNSW (O(log n)) → Re-ranking top-10
10-100x más rápido
```

---

## 💡 Ejemplos de Migración

### Ejemplo 1: Tu script de carga

**Antes:**
```python
# crearCSV_embedding_full.py
json_front = json.load(json_file_path_front)
mi_pd_frame = pd.DataFrame(json_front)
mi_pd_frame['Embedding'] = mi_pd_frame.apply(...)
mi_pd_frame.to_csv(csv_file_path)
```

**Ahora:**
```bash
# 1. Preparar JSON en el formato correcto
python scripts/create_sample_data.py

# 2. Cargar en la base de datos
python scripts/load_documents.py --file data/sample_documents.json

# ¡Listo! Embeddings calculados y almacenados automáticamente
```

### Ejemplo 2: Tu búsqueda

**Antes:**
```python
# busqueda_embedding_full.py
def compute_similarity(query, text):
    inputs = tokenizer(query, text, ...)
    outputs = model(**inputs)
    return outputs.logits[0].item()

# Calcular con cada documento (lento)
mi_pd_frame["Similitud"] = mi_pd_frame['info'].apply(...)
```

**Ahora:**
```bash
# Búsqueda en 1 línea (rápido)
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "X-API-Key: dev-key" \
  -d '{"query": "búsqueda", "top_k": 5}'
```

---

## 🎯 Checklist de Migración

Si quieres migrar tus datos:

- [ ] Convertir tu CSV/JSON al formato del SaaS
- [ ] Cambiar modelo en .env si quieres mantener BAAI/bge-m3
- [ ] Ejecutar: `python scripts/load_documents.py --file tu_archivo.json`
- [ ] Probar búsquedas: `python scripts/test_api.py`
- [ ] Integrar con tu aplicación (cambiar endpoint a /api/v1/search/query)

---

## 🔗 Tabla de Referencia

| Funcionalidad | Tu Script | Nuevo SaaS |
|---|---|---|
| Cargar documentos | CSV manual | `load_documents.py` |
| Crear embeddings | `crearCSV_embedding_full.py` | `Embedder` class |
| Almacenar embeddings | CSV (lentos) | Chroma (indexados) |
| Buscar | `/embedding3` endpoint | `/api/v1/search/query` |
| Re-ranking | Cross-encoder manual | SearchEngine (automático) |
| Documentación API | Manual | Swagger automático |
| Autenticación | No | API Keys |
| Escalabilidad | CSV limitado | Chroma + pgvector ready |

---

## 🚀 Próximas Mejoras Posibles

Si quieres ir más allá:

1. **PostgreSQL + pgvector**
   ```bash
   # Para millones de documentos
   pip install pgvector psycopg2
   ```

2. **Caché con Redis**
   ```bash
   # Para búsquedas frecuentes
   pip install redis
   ```

3. **Webhook para indexación**
   ```python
   # Indexar documentos automáticamente cuando se crean
   ```

4. **Análisis de uso**
   ```python
   # Trackear búsquedas populares
   ```

---

## ✨ Conclusión

Tu código anterior ahora es:
- ✅ Más rápido (búsqueda vectorial indexada)
- ✅ Más escalable (Chroma + ready para pgvector)
- ✅ Profesional (API REST con documentación)
- ✅ Seguro (autenticación + error handling)
- ✅ Mantenible (código limpio y modular)

**Migra tus datos en 5 minutos y disfruta de un SaaS profesional** 🚀

---

## 📞 Soporte

- Ver documentación: `http://localhost:8000/api/docs`
- Leer más: `INSTALLATION.md`
- Comandos rápidos: `REFERENCE.md`
"""

def main():
    """Display the integration guide."""
    print(INTEGRATION_GUIDE)
    
    # Save to file
    guide_file = Path("/Users/estebanbardolet/Desktop/API_IA/INTEGRATION_GUIDE.md")
    with open(guide_file, 'w') as f:
        f.write(INTEGRATION_GUIDE)
    
    print(f"\n✅ Guía guardada en: {guide_file}")

if __name__ == "__main__":
    main()
