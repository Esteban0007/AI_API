# 🚀 Semantic Search SaaS - Proyecto Completado

Felicidades! Tu plataforma SaaS de búsqueda semántica está lista. Aquí está toda la información que necesitas.

## 📁 Estructura del Proyecto

```
API_IA/
├── 📂 app/                           # Código principal
│   ├── 📂 api/v1/                   # Endpoints REST
│   │   ├── documents.py             # Carga y gestión de documentos
│   │   ├── search.py                # Búsqueda y re-ranking
│   │   └── users.py                 # Gestión de usuarios (SaaS)
│   ├── 📂 core/                     # Configuración y seguridad
│   │   ├── config.py                # Configuración centralizada
│   │   └── security.py              # Autenticación
│   ├── 📂 engine/                   # Núcleo de búsqueda
│   │   ├── embedder.py              # Generación de embeddings
│   │   ├── store.py                 # Base de datos vectorial
│   │   └── searcher.py              # Búsqueda + re-ranking
│   ├── 📂 models/                   # Esquemas Pydantic
│   │   ├── document.py              # Modelos de documentos
│   │   └── search.py                # Modelos de búsqueda
│   └── main.py                      # Aplicación FastAPI
├── 📂 scripts/                       # Utilidades
│   ├── load_json.py                 # Cargar documentos
│   ├── rebuild_index.py             # Reconstruir índice
│   └── create_sample_data.py        # Generar datos de prueba
├── 📂 data/                          # Datos y base de datos
│   └── chroma_db/                   # Base vectorial (creada al ejecutar)
├── 📂 tests/                         # Tests
│   └── test_example.py              # Test de verificación
├── requirements.txt                 # Dependencias Python
├── .env.example                     # Plantilla de configuración
├── .gitignore                       # Archivos ignorados
├── README.md                        # Documentación completa
├── QUICKSTART.md                    # Guía rápida
├── DEPLOYMENT.md                    # Guía de deployment
└── SETUP.md                         # Este archivo

```

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐
│   Cliente   │ (Frontend/Mobile/CLI)
└──────┬──────┘
       │ HTTP(S)
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│  • CORS Middleware                      │
│  • Request Logging                      │
│  • Error Handling                       │
└──────┬──────────────────────────────────┘
       │
       ├─ POST /api/v1/documents/upload
       │   ↓
       │   [Validación de Documentos]
       │   ↓
       │   [Embedder] → Generar embeddings
       │   ↓
       │   [VectorStore] → Guardar en Chroma
       │
       ├─ POST /api/v1/search/query
       │   ↓
       │   [Embedder] → Embedding de query
       │   ↓
       │   [VectorStore] → Búsqueda ANN (top-k)
       │   ↓
       │   [SearchEngine] → Re-ranking con Cross-Encoder
       │   ↓
       │   Devolver resultados ordenados
       │
       └─ GET /api/v1/documents/stats
           ↓
           [VectorStore] → Estadísticas

┌─────────────────────────────────────────┐
│     Data Layer - Chroma Database        │
├─────────────────────────────────────────┤
│  • Embeddings (vectores)                │
│  • Metadatos de documentos              │
│  • Contenido original                   │
│  • Persistencia en disco                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      External Models (HuggingFace)      │
├─────────────────────────────────────────┤
│  • Sentence Transformers (embeddings)   │
│  • Cross-Encoder (re-ranking)           │
│  • Descargados la primera vez           │
└─────────────────────────────────────────┘
```

## 🔧 Instalación Paso a Paso

### 1. Preparar el Entorno

```bash
# Ir al directorio del proyecto
cd /Users/estebanbardolet/Desktop/API_IA

# Crear entorno virtual
python3 -m venv venv

# Activar entorno (en macOS/Linux)
source venv/bin/activate

# En Windows usa:
# venv\Scripts\activate
```

### 2. Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt
```

La primera instalación descargará los modelos (~1-2 GB):

- `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
- `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (re-ranking)

### 3. Verificar Instalación

```bash
# Ejecutar test de ejemplo
python tests/test_example.py
```

Verás algo como:

```
✅ Embedder working. Shape: (384,)
✅ VectorStore working. Document added successfully.
✅ SearchEngine working. Found 2 results in 125.45ms
✅ All tests passed! Installation is correct.
```

## 🚀 Ejecutar la Aplicación

### Opción 1: Desarrollo (con recargas automáticas)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Producción

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Opción 3: Docker (si tienes Docker instalado)

```bash
# Crear imagen
docker build -t semantic-search .

# Ejecutar contenedor
docker run -p 8000:8000 -v $(pwd)/data:/app/data semantic-search
```

## 📊 Cargar Datos

### Crear Datos de Ejemplo

```bash
python scripts/create_sample_data.py
```

Genera 5 documentos de ejemplo en `data/sample_documents.json`

### Cargar en la Base de Datos

```bash
python scripts/load_json.py data/sample_documents.json
```

Output esperado:

```
✅ Loaded 5 documents from data/sample_documents.json
✅ Successfully uploaded: 5
✅ Failed uploads: 0
Collection Statistics:
  collection_name: documents
  document_count: 5
  embedding_dimension: 384
  model: sentence-transformers/all-MiniLM-L6-v2
```

## 🔍 Probar la API

### 1. Interfaz Web Interactiva

Abre en tu navegador:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

Aquí puedes:

- ✅ Probar endpoints directamente
- 📖 Ver documentación de parámetros
- 📝 Ver ejemplos de request/response
- 🧪 Generar código en diferentes lenguajes

### 2. Con curl

```bash
# Búsqueda
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo funciona el aprendizaje automático?",
    "top_k": 3
  }'

# Ver estadísticas
curl "http://localhost:8000/api/v1/documents/stats"

# Health check
curl "http://localhost:8000/api/v1/search/health"
```

### 3. Con Python

```python
import requests

# Búsqueda
response = requests.post(
    "http://localhost:8000/api/v1/search/query",
    json={
        "query": "máquinas que aprenden",
        "top_k": 5
    }
)

results = response.json()
print(f"Encontrados: {results['total_results']} resultados")
print(f"Tiempo: {results['execution_time_ms']:.2f}ms")

for result in results['results']:
    print(f"\n📄 {result['title']}")
    print(f"   Score: {result['score']:.2f}")
    print(f"   ID: {result['id']}")
```

### 4. Con JavaScript/Node.js

```javascript
// Instalando axios: npm install axios

const axios = require("axios");

async function search() {
  try {
    const response = await axios.post(
      "http://localhost:8000/api/v1/search/query",
      {
        query: "algoritmos de aprendizaje",
        top_k: 5,
      }
    );

    console.log("Resultados:", response.data.results);
  } catch (error) {
    console.error("Error:", error);
  }
}

search();
```

## ⚙️ Configuración Avanzada

### Cambiar Modelos

Edita `app/core/config.py`:

```python
# Opción 1: Más rápido (recomendado)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Opción 2: Más preciso
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIMENSION = 768

# Opción 3: Multilingüe
EMBEDDING_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v2"
EMBEDDING_DIMENSION = 512
```

### Ajustar Parámetros de Búsqueda

```python
TOP_K = 10           # Candidatos antes de re-ranking
RERANK_TOP_K = 5     # Resultados finales
```

### Puerto y Host

```python
HOST = "0.0.0.0"     # Interfaz a escuchar
PORT = 8000          # Puerto
DEBUG = True         # Modo debug
```

## 🐛 Resolución de Problemas

### Problema: "No module named 'sentence_transformers'"

```bash
pip install sentence-transformers torch transformers
```

### Problema: "Chroma database locked"

```bash
rm -rf data/chroma_db
# Se recreará automáticamente
```

### Problema: Búsquedas muy lentas

1. **Verificar si hay GPU disponible**:

```python
import torch
print(torch.cuda.is_available())  # Debe ser True
```

2. **Usar modelo más ligero** (si no hay GPU):

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

3. **Reducir TOP_K** para menos re-ranking:

```python
TOP_K = 5
```

### Problema: Resultados poco relevantes

- Aumentar `TOP_K` (ej: de 10 a 20)
- Cambiar a modelo más preciso
- Mejorar la calidad del contenido de documentos
- Aumentar el número de documentos

## 📈 Escalar la Aplicación

### Fase 1: Prototipo (Actual - hasta 10K documentos)

- Una sola instancia
- Chroma en disco local
- Perfecto para MVP y testing

### Fase 2: Producción Pequeña (10K-100K documentos)

- Múltiples instancias con carga balanceada
- Chroma en NFS o S3
- Nginx como proxy reverso
- Monitoreo básico

### Fase 3: Producción Grande (100K+ documentos)

- Migrar a Qdrant o Weaviate
- Kubernetes para orquestación
- Redis para caching
- ElasticSearch para búsqueda híbrida

### Fase 4: SaaS Completo

- Múltiples tenants
- Autenticación robusta (OAuth2)
- Restricciones de cuota
- Billing integrado
- CDN global

## 🔐 Seguridad

### Habilitar HTTPS

```bash
# Generar certificados autofirmados para testing
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Ejecutar con HTTPS
uvicorn app.main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### Implementar Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/search")
@limiter.limit("10/minute")
async def search(...):
    ...
```

### Validación de API Keys

Ya viene implementada en `app/core/security.py`. En producción:

1. Guardar keys en base de datos
2. Hashear con bcrypt
3. Implementar rotación de keys
4. Monitorear acceso

## 📚 Recursos Útiles

- **Documentación de FastAPI**: https://fastapi.tiangolo.com/
- **Sentence Transformers**: https://www.sbert.net/
- **Chroma DB**: https://www.trychroma.com/
- **Cross-Encoders**: https://www.sbert.net/docs/usage/cross_encoders/

## 📝 Próximos Pasos

1. **Personalizar tu búsqueda**

   - Entrena modelos propios con tus datos
   - Agrega análisis de sentimiento
   - Implementa búsqueda hibrida (vectorial + keyword)

2. **Integrar con tu aplicación**

   - Frontend con React/Vue
   - Dashboard de administración
   - API gateway

3. **Monetizar como SaaS**

   - Planes de precios
   - Billing y pagos
   - Análitica de uso

4. **Escalar a producción**
   - Desplegar en AWS/GCP/Azure
   - Configurar monitoreo (Datadog, New Relic)
   - Implementar CI/CD (GitHub Actions, GitLab CI)

## ✅ Checklist Final

- [ ] Instaladas todas las dependencias
- [ ] Test de ejemplo pasó correctamente
- [ ] Datos de ejemplo cargados
- [ ] Servidor iniciado sin errores
- [ ] Accedí a /api/docs y funcionó
- [ ] Realicé búsquedas de prueba
- [ ] Estatísticas muestran documentos cargados

## 🎉 ¡Listo!

Tu plataforma SaaS de búsqueda semántica está lista para:

- ✨ Búsquedas semánticas precisas
- 🚀 Escalabilidad
- 🔒 Seguridad
- 💼 Monetización SaaS

¿Preguntas o necesitas ayuda? Revisa:

- `README.md` para documentación completa
- `QUICKSTART.md` para ejemplos rápidos
- `DEPLOYMENT.md` para guía de producción
- `/api/docs` para documentación interactiva

¡Que disfrutes construyendo! 🚀
