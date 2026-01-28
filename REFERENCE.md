# 📚 Índice de Referencia Rápida - Semantic Search SaaS

## 📖 Documentación

| Archivo           | Propósito                       | Para Quién                    |
| ----------------- | ------------------------------- | ----------------------------- |
| **SETUP.md**      | Guía completa de instalación    | Primeros pasos, principiantes |
| **QUICKSTART.md** | Guía rápida de 10 minutos       | Quiero empezar ya             |
| **README.md**     | Documentación técnica completa  | Desarrolladores               |
| **DEPLOYMENT.md** | Guía de deployment a producción | DevOps, desarrollo            |
| **Este archivo**  | Índice y referencias rápidas    | Búsqueda rápida               |

## 🗂️ Estructura de Carpetas

```
app/
├── api/v1/          → Endpoints REST (POST /search, POST /documents)
├── core/            → Configuración y autenticación
├── engine/          → Núcleo: embeddings, búsqueda, re-ranking
├── models/          → Esquemas Pydantic
├── db/              → Conexiones a base de datos
└── main.py          → Aplicación FastAPI

scripts/
├── load_json.py     → Cargar documentos desde JSON
├── rebuild_index.py → Reconstruir índice completo
└── create_sample_data.py → Generar datos de ejemplo

tests/
└── test_example.py  → Tests de verificación

data/
└── chroma_db/       → Base de datos vectorial (generada)
```

## 🔧 Comandos Útiles

### Instalación

```bash
# Instalación automática (recomendado)
chmod +x setup.sh && ./setup.sh

# O manual:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Ejecutar la Aplicación

```bash
# Desarrollo (con hot-reload)
uvicorn app.main:app --reload

# Producción
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

# Especificar puerto
uvicorn app.main:app --port 9000
```

### Gestionar Datos

```bash
# Crear datos de ejemplo
python scripts/create_sample_data.py

# Cargar documentos
python scripts/load_json.py data/documentos.json

# Reconstruir índice (limpia datos antiguos)
python scripts/rebuild_index.py --source data/documentos.json
```

### Testing

```bash
# Verificar instalación
python tests/test_example.py

# Run pytest
pytest tests/ -v

# Ver coverage
pytest tests/ --cov=app
```

## 🔌 Endpoints REST

### POST /api/v1/search/query

**Búsqueda semántica**

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo funciona?",
    "top_k": 5
  }'
```

### POST /api/v1/documents/upload

**Cargar documentos**

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [{"id": "doc-1", "title": "...", "content": "..."}]
  }'
```

### GET /api/v1/documents/stats

**Ver estadísticas**

```bash
curl "http://localhost:8000/api/v1/documents/stats"
```

### GET /api/v1/search/health

**Verificar estado**

```bash
curl "http://localhost:8000/api/v1/search/health"
```

### DELETE /api/v1/documents/{doc_id}

**Eliminar documento**

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/doc-1"
```

## 🎯 Configuración

### Variables Principales (app/core/config.py)

| Variable                   | Valor Actual                   | Descripción                    |
| -------------------------- | ------------------------------ | ------------------------------ |
| `EMBEDDING_MODEL`          | `all-MiniLM-L6-v2`             | Modelo para embeddings         |
| `EMBEDDING_DIMENSION`      | `384`                          | Dimensión de embeddings        |
| `TOP_K`                    | `10`                           | Candidatos antes de re-ranking |
| `RERANK_TOP_K`             | `5`                            | Resultados finales             |
| `RERANK_MODEL`             | `mmarco-mMiniLMv2-L12-H384-v1` | Modelo de re-ranking           |
| `CHROMA_PERSIST_DIRECTORY` | `./data/chroma_db`             | Ubicación de BD                |
| `PORT`                     | `8000`                         | Puerto del servidor            |
| `DEBUG`                    | `True`                         | Modo debug                     |

## 📊 Pipeline de Búsqueda

```
1. Cliente envía: {"query": "texto"}
                            ↓
2. Servidor genera embedding de query
                            ↓
3. Búsqueda vectorial ANN → top-10 candidatos
                            ↓
4. Re-ranking con Cross-Encoder
                            ↓
5. Devuelve top-5 resultados ordenados
                            ↓
6. Cliente recibe: [{"id": "...", "score": 0.95, ...}]
```

## 🚀 Casos de Uso

### Para Documentación

```json
{
  "id": "doc-manual-001",
  "title": "Manual de Usuario",
  "content": "Este es el contenido del manual...",
  "metadata": {
    "category": "documentacion",
    "language": "es",
    "source": "manual.pdf"
  }
}
```

### Para Noticias

```json
{
  "id": "news-001",
  "title": "Noticia de Hoy",
  "content": "Última noticia sobre...",
  "metadata": {
    "category": "noticias",
    "language": "es",
    "source": "https://news.com"
  }
}
```

### Para FAQ

```json
{
  "id": "faq-001",
  "title": "¿Cómo debo proceder?",
  "content": "Para hacer X debes seguir estos pasos...",
  "keywords": ["proceso", "pasos"],
  "metadata": {
    "category": "faq",
    "language": "es"
  }
}
```

## 🐛 Troubleshooting Rápido

| Problema              | Solución                              |
| --------------------- | ------------------------------------- |
| `ModuleNotFoundError` | `pip install -r requirements.txt`     |
| BD bloqueada          | `rm -rf data/chroma_db`               |
| Búsquedas lentas      | Usar modelo más ligero o GPU          |
| Resultados pobres     | Aumentar `TOP_K` o mejorar documentos |
| Puerto 8000 ocupado   | `uvicorn app.main:app --port 9000`    |
| Memoria insuficiente  | Usar `all-MiniLM-L6-v2` (ligero)      |

## 🔗 Links Útiles

- **API Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json
- **Sentence Transformers**: https://www.sbert.net/
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## 📈 Roadmap Típico

1. **Semana 1**: Instalar, cargar datos, búsquedas básicas
2. **Semana 2**: Integrar en tu aplicación, ajustar modelos
3. **Semana 3**: Deployment en servidor, configurar HTTPS
4. **Semana 4**: Optimizaciones, escalar a más datos
5. **Mes 2+**: SaaS completo, múltiples tenants, monetización

## 💡 Tips de Productividad

1. **Actualiza modelos sin perder datos**:

   ```bash
   # Edita config.py con nuevo modelo
   python scripts/rebuild_index.py --source data/backup.json
   ```

2. **Monitorea estadísticas en tiempo real**:

   ```bash
   watch -n 2 'curl -s http://localhost:8000/api/v1/documents/stats | python -m json.tool'
   ```

3. **Carga muchos documentos**:

   ```bash
   python scripts/load_json.py large_file.json  # Automático en paralelo
   ```

4. **Prueba diferentes queries fácilmente**:
   - Usa http://localhost:8000/api/docs
   - Test en los formularios interactivos
   - Copiar cuRL para debugging

## 📞 Soporte

- **Documentación**: Ver archivos .md en la raíz
- **Errores específicos**: Ver `README.md` sección Troubleshooting
- **Deployment**: Ver `DEPLOYMENT.md`
- **Ejemplos**: Ver `QUICKSTART.md`

---

**Última actualización**: 2025-11-23
**Versión**: 1.0.0
