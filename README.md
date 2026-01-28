# Semantic Search SaaS API

Una plataforma moderna de búsqueda semántica basada en FastAPI que combina embeddings vectoriales con re-ranking mediante cross-encoders para resultados altamente relevantes.

## Características

✨ **Búsqueda Semántica Avanzada**

- Embeddings generados con Sentence Transformers
- Re-ranking inteligente usando cross-encoders
- Búsqueda vectorial ultrarrápida con Chroma
- Resultados ordenados por relevancia

🚀 **Arquitectura SaaS Lista**

- API REST completamente documentada
- Sistema de autenticación con API Keys
- Límites de cuota y tracking de uso
- Facilidad para escalar a múltiples inquilinos

📊 **Gestión de Documentos**

- Carga por lotes de documentos JSON
- Almacenamiento persistente de vectores
- Metadatos flexibles por documento
- Re-indexación bajo demanda

## Estructura del Proyecto

```
project/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── search.py        # Endpoints de búsqueda
│   │   │   ├── documents.py     # Endpoints de documentos
│   │   │   └── users.py         # Endpoints de usuarios (SaaS)
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py            # Configuración centralizada
│   │   ├── security.py          # Autenticación y seguridad
│   │   └── __init__.py
│   ├── engine/
│   │   ├── embedder.py          # Generador de embeddings
│   │   ├── searcher.py          # Motor de búsqueda + re-ranking
│   │   ├── store.py             # Almacenamiento vectorial
│   │   └── __init__.py
│   ├── models/
│   │   ├── document.py          # Modelos de documentos
│   │   ├── search.py            # Modelos de búsqueda
│   │   └── __init__.py
│   ├── main.py                  # Aplicación FastAPI
│   └── __init__.py
├── scripts/
│   ├── load_json.py             # Cargar documentos desde JSON
│   └── rebuild_index.py         # Reconstruir índice
├── data/
│   └── chroma_db/               # Base de datos vectorial persistente
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Instalación

### Requisitos Previos

- Python 3.9+
- pip

### Configuración del Entorno

1. **Clonar/descargar el proyecto**

```bash
cd /ruta/a/proyecto
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Uso

### Iniciar el Servidor

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción (con Gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

El servidor estará disponible en `http://localhost:8000`

### Acceder a la Documentación

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### 🔍 Búsqueda

**POST `/api/v1/search/query`**

Realizar una búsqueda semántica con re-ranking.

```json
{
  "query": "¿Cómo funciona el aprendizaje automático?",
  "top_k": 5,
  "include_content": true
}
```

**Response:**

```json
{
  "query": "¿Cómo funciona el aprendizaje automático?",
  "total_results": 3,
  "results": [
    {
      "id": "doc-001",
      "title": "Fundamentos de ML",
      "score": 0.94,
      "content": "El aprendizaje automático es...",
      "metadata": {
        "category": "tutorial",
        "language": "es"
      }
    }
  ],
  "execution_time_ms": 125.5
}
```

**GET `/api/v1/search/health`**

Verificar estado del servicio de búsqueda.

### 📄 Documentos

**POST `/api/v1/documents/upload`**

Cargar documentos para indexación.

```json
{
  "documents": [
    {
      "id": "doc-001",
      "title": "Título del Contenido",
      "content": "Texto completo del documento...",
      "keywords": ["ml", "ai"],
      "metadata": {
        "category": "tutorial",
        "language": "es",
        "source": "https://example.com/article-1"
      }
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Successfully uploaded 10 documents",
  "uploaded_count": 10,
  "failed_count": 0
}
```

**GET `/api/v1/documents/stats`**

Obtener estadísticas de la colección.

```json
{
  "collection_name": "documents",
  "document_count": 150,
  "embedding_dimension": 384,
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

**DELETE `/api/v1/documents/{doc_id}`**

Eliminar un documento específico.

### 👤 Usuarios (Placeholder SaaS)

**GET `/api/v1/users/me`**

Obtener información del usuario actual.

**GET `/api/v1/users/quota`**

Obtener cuota de uso y consumo actual.

## Scripts Auxiliares

### Cargar Documentos desde JSON

```bash
python scripts/load_json.py data/documentos.json
```

El archivo JSON puede tener este formato:

```json
[
  {
    "id": "doc-001",
    "title": "Documento 1",
    "content": "Contenido del documento...",
    "keywords": ["keyword1", "keyword2"],
    "metadata": {
      "category": "tutorial",
      "language": "es",
      "source": "https://..."
    }
  }
]
```

O con una clave `documents`:

```json
{
  "documents": [...]
}
```

### Reconstruir Índice

Reconstruye todos los embeddings desde una fuente JSON:

```bash
python scripts/rebuild_index.py --source documentos.json --backup
```

Opciones:

- `--source`: Archivo JSON de origen (requerido)
- `--backup`: Crear backup antes de reconstruir (por defecto: true)
- `--no-backup`: Saltar creación de backup

## Configuración

### Variables de Entorno

Edita `.env` para personalizar:

```env
# API Configuration
API_TITLE=Semantic Search SaaS API
PORT=8000
DEBUG=true

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# Search Configuration
TOP_K=10                    # Candidatos antes de re-ranking
RERANK_TOP_K=5             # Resultados finales
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1

# Database
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

### Cambiar Modelos

Para usar diferentes modelos de embeddings y re-ranking:

**Embeddings ligeros (rápido):**

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

**Embeddings más precisos:**

```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DIMENSION=768
```

**Cross-Encoders:**

```env
RERANK_MODEL=cross-encoder/ms-marco-MiniLM-L-12-v2
```

## Pipeline de Búsqueda

1. **Embedding de Query**: Convertir la query a vector
2. **Búsqueda Vectorial**: Recuperar los K documentos más similares usando cosine similarity
3. **Re-ranking**: Evaluar pares (query, documento) con cross-encoder para mayor precisión
4. **Ordenamiento**: Devolver documentos ordenados por score final

```
User Query
    ↓
[Embedder] → Query Vector
    ↓
[Vector Search] → Top K Candidates
    ↓
[Cross-Encoder] → Re-ranked Scores
    ↓
[Results] → Final Top K Results
```

## Ejemplo de Uso Completo

### 1. Cargar Documentos

```bash
# Crear archivo de ejemplo
cat > data/ejemplo.json << 'EOF'
[
  {
    "id": "doc-001",
    "title": "Introducción a Machine Learning",
    "content": "Machine Learning es una rama de la inteligencia artificial que permite a las máquinas aprender de los datos sin ser programadas explícitamente...",
    "keywords": ["ml", "ai", "learning"],
    "metadata": {
      "category": "tutorial",
      "language": "es"
    }
  },
  {
    "id": "doc-002",
    "title": "Redes Neuronales Profundas",
    "content": "Las redes neuronales profundas son el núcleo del deep learning moderno...",
    "keywords": ["neural", "deep-learning"],
    "metadata": {
      "category": "advanced",
      "language": "es"
    }
  }
]
EOF

# Cargar documentos
python scripts/load_json.py data/ejemplo.json
```

### 2. Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

### 3. Realizar Búsquedas

```bash
# Usando curl
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo funciona el aprendizaje automático?",
    "top_k": 5
  }'

# O con Python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search/query",
    json={
        "query": "¿Cómo funciona el aprendizaje automático?",
        "top_k": 5
    }
)

print(response.json())
```

## Rendimiento

### Benchmarks Esperados

Con hardware moderno (GPU):

- **Generación de embeddings**: ~100-500 docs/segundo
- **Búsqueda vectorial**: <100ms para 10K documentos
- **Re-ranking**: ~50-200ms por query (depende de TOP_K)
- **Latencia total**: 100-300ms por búsqueda

Con CPU:

- **Generación de embeddings**: ~10-50 docs/segundo
- **Búsqueda vectorial**: <50ms
- **Re-ranking**: 200-500ms

### Optimizaciones

1. **Usar GPU**: Configure CUDA si está disponible
2. **Modelos más ligeros**: Use `all-MiniLM-L6-v2` para mejor velocidad
3. **Batch processing**: Cargue documentos en lotes grandes
4. **Índices apropiados**: Chroma optimiza automáticamente

## Arquitectura y Escalabilidad

### Para Múltiples Tenants

1. Crear collections separadas por tenant:

```python
vector_store = VectorStore(collection_name=f"documents_{tenant_id}")
```

2. Agregar validación de tenant en endpoints:

```python
@router.post("/api/v1/{tenant_id}/documents/upload")
async def upload_documents(tenant_id: str, ...):
    # Validar tenant
    # Usar collection específica del tenant
```

3. Implementar tracking de uso por tenant

### Para Mayor Volumen

1. **Shard por categoría**: Colecciones separadas por tipo de contenido
2. **Cache de resultados**: Caché Redis para queries populares
3. **Load balancing**: Múltiples instancias con balanceador de carga
4. **DB escalable**: Migrar a Qdrant o Weaviate para producción masiva

## Troubleshooting

### Error: "Module not found"

```bash
# Asegurar que el entorno virtual está activado
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Chroma database locked"

```bash
# Eliminar archivos de bloqueo
rm -rf data/chroma_db/.lock
```

### Resultados pobres de búsqueda

1. Revisar que los documentos tengan contenido suficiente
2. Aumentar TOP_K antes de re-ranking
3. Considerar cambiar el modelo de embeddings a uno más preciso

### Lentitud en búsquedas

1. Verificar que se esté usando GPU si está disponible
2. Reducir TOP_K para menos re-ranking
3. Usar modelo de embedding más ligero

## Licencia

MIT

## Autor

Proyecto generado para SaaS de búsqueda semántica.
