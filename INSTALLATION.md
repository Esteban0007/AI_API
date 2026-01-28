# 🎯 Guía de Instalación y Ejecución - Semantic Search SaaS

## ✅ Verificación del Proyecto

Tu proyecto FastAPI SaaS de búsqueda semántica está **100% completo**. Aquí está lo que hemos creado:

### 📁 Estructura del Proyecto

```
API_IA/
├── app/
│   ├── api/v1/
│   │   ├── documents.py      ✅ Endpoints de carga de documentos
│   │   ├── search.py         ✅ Endpoints de búsqueda semántica
│   │   └── users.py          ✅ Endpoints de usuarios (SaaS)
│   ├── engine/
│   │   ├── embedder.py       ✅ Generador de embeddings (HuggingFace)
│   │   ├── searcher.py       ✅ Motor de búsqueda + re-ranking
│   │   └── store.py          ✅ Almacenamiento vectorial (Chroma)
│   ├── models/
│   │   ├── document.py       ✅ Modelos de documentos
│   │   └── search.py         ✅ Modelos de búsqueda
│   ├── core/
│   │   ├── config.py         ✅ Configuración centralizada
│   │   └── security.py       ✅ Autenticación con API Keys
│   └── main.py               ✅ Aplicación FastAPI
│
├── scripts/
│   ├── create_sample_data.py  ✅ Crear documentos de ejemplo
│   ├── load_documents.py      ✅ Cargar documentos en BD vectorial
│   ├── load_json.py           ✅ Cargar desde JSON
│   ├── rebuild_index.py       ✅ Reconstruir índice
│   ├── run_server.py          ✅ Iniciar servidor
│   └── test_api.py            ✅ Suite de tests
│
├── requirements.txt           ✅ Dependencias
├── .env.example               ✅ Variables de entorno
├── .gitignore                 ✅ Configuración Git
└── README.md                  ✅ Documentación principal
```

## 🚀 Instalación Paso a Paso

### Paso 1: Crear Entorno Virtual

```bash
cd /Users/estebanbardolet/Desktop/API_IA

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

**En Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### Paso 2: Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar todas las dependencias
pip install -r requirements.txt
```

Esto instalará:

- **FastAPI** - Framework web moderno
- **Uvicorn** - Servidor ASGI
- **Sentence Transformers** - Embeddings de HuggingFace
- **Chroma** - Base de datos vectorial
- **Transformers** - Para cross-encoders
- **Pydantic** - Validación de datos
- Y más...

**Tiempo estimado:** 10-15 minutos (depende de tu conexión)

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# (Opcional) Editar .env si necesitas cambios
# nano .env   # o usa tu editor favorito
```

El archivo `.env` contiene la configuración por defecto, que está lista para usar.

## 🎯 Ejecutar el Proyecto

### Opción A: Usar el Script Incluido (Recomendado)

```bash
# Asegúrate de estar en el directorio y con el entorno activado
cd /Users/estebanbardolet/Desktop/API_IA
source venv/bin/activate

# Ejecutar servidor
python scripts/run_server.py
```

Deberías ver:

```
╔════════════════════════════════════════╗
║  Semantic Search SaaS - FastAPI Server ║
╚════════════════════════════════════════╝

📌 API Title: Semantic Search SaaS API
📌 Version: 1.0.0
📌 Server: 0.0.0.0:8000
📌 Debug: True

🚀 Starting server...
📖 Docs: http://localhost:8000/api/docs
```

### Opción B: Usar Uvicorn Directamente

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 Acceder a la API

Una vez que el servidor está corriendo:

**Swagger UI (Recomendado):**

```
http://localhost:8000/api/docs
```

**ReDoc:**

```
http://localhost:8000/api/redoc
```

**OpenAPI JSON:**

```
http://localhost:8000/api/openapi.json
```

## 📥 Cargar Documentos de Prueba

En **otra terminal** (con el entorno activado):

```bash
cd /Users/estebanbardolet/Desktop/API_IA
source venv/bin/activate

# 1. Crear documentos de ejemplo
python scripts/create_sample_data.py

# 2. Indexarlos
python scripts/load_documents.py --file data/sample_documents.json

# 3. Verificar que se cargaron
curl -X GET "http://localhost:8000/api/v1/documents/stats" \
  -H "X-API-Key: dev-key"
```

Deberías ver:

```json
{
  "collection_name": "documents",
  "document_count": 6,
  "embedding_dimension": 384,
  "model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

## 🔍 Hacer tu Primera Búsqueda

### Con cURL

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es el machine learning?",
    "top_k": 5,
    "include_content": true
  }'
```

### Con Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search/query",
    json={
        "query": "¿Qué es el machine learning?",
        "top_k": 5,
        "include_content": True
    },
    headers={"X-API-Key": "dev-key"}
)

results = response.json()
for result in results['results']:
    print(f"📄 {result['title']}: {result['score']:.4f}")
```

### Con el Script de Test

```bash
python scripts/test_api.py
```

## 📤 Cargar tus Propios Documentos

### Crear archivo JSON (documentos.json)

```json
{
  "documents": [
    {
      "id": "mi-doc-1",
      "title": "Titulo del documento",
      "content": "Este es el contenido completo que será indexado para búsqueda semántica. Puede ser un párrafo, un artículo, una página web, etc.",
      "keywords": ["palabra-clave", "tag"],
      "metadata": {
        "category": "tutorial",
        "language": "es",
        "source": "https://ejemplo.com"
      }
    }
  ]
}
```

### Cargar los documentos

```bash
python scripts/load_documents.py --file documentos.json
```

## ⚙️ Ajustar Configuración

Edita el archivo `.env` para cambiar:

```env
# Puerto del servidor
PORT=8000

# Modelos de IA
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1

# Búsqueda
TOP_K=10              # Candidatos antes de re-ranking
RERANK_TOP_K=5        # Resultados finales

# Directorio de datos
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

## 🧪 Ejecutar Tests

```bash
# Suite completa de tests
python scripts/test_api.py

# Debería mostrar:
# ✅ PASSED - Upload Documents
# ✅ PASSED - Search
# ✅ PASSED - Statistics
# ✅ PASSED - Health Check
```

## 📊 Comandos Útiles

```bash
# Health check
curl -X GET "http://localhost:8000/api/v1/search/health" \
  -H "X-API-Key: dev-key"

# Estadísticas de documentos
curl -X GET "http://localhost:8000/api/v1/documents/stats" \
  -H "X-API-Key: dev-key"

# Eliminar un documento
curl -X DELETE "http://localhost:8000/api/v1/documents/doc-001" \
  -H "X-API-Key: dev-key"

# Limpiar toda la colección
python scripts/rebuild_index.py

# Ver usuario actual (SaaS)
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "X-API-Key: dev-key"

# Ver cuota de uso (SaaS)
curl -X GET "http://localhost:8000/api/v1/users/quota" \
  -H "X-API-Key: dev-key"
```

## 🐛 Solucionar Problemas

### "ModuleNotFoundError: No module named 'app'"

```bash
# Asegúrate de:
# 1. Estar en el directorio correcto
cd /Users/estebanbardolet/Desktop/API_IA

# 2. Tener el entorno activado
source venv/bin/activate

# 3. Haber instalado dependencias
pip install -r requirements.txt
```

### "Port 8000 already in use"

```bash
# Opción 1: Usar otro puerto
uvicorn app.main:app --port 8001

# Opción 2: Liberar el puerto
lsof -i :8000
kill -9 <PID>
```

### "Model downloading..." tarda mucho

```bash
# Los modelos se descargan automáticamente en la primera ejecución
# - all-MiniLM-L6-v2: ~22MB
# - mmarco-mMiniLMv2-L12-H384-v1: ~500MB
# Total: ~500MB, espera 5-10 minutos en la primera ejecución
```

### No hay resultados en búsqueda

```bash
# Verifica que hay documentos indexados
curl -X GET "http://localhost:8000/api/v1/documents/stats" \
  -H "X-API-Key: dev-key"

# Si dice "document_count": 0, carga documentos:
python scripts/create_sample_data.py
python scripts/load_documents.py --file data/sample_documents.json
```

## 📈 Siguiente Paso: Producción

Para desplegar en producción:

1. **Usar una base de datos permanente**

   ```bash
   # PostgreSQL con pgvector
   pip install pgvector psycopg2-binary
   ```

2. **Usar servidor ASGI de producción**

   ```bash
   pip install gunicorn
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

3. **Docker**

   ```dockerfile
   FROM python:3.10
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

4. **Variables de entorno seguras**
   ```bash
   # Usar secretos en lugar de .env en producción
   export API_KEY_SECRET="tu-clave-secreta"
   ```

## 📚 Documentación Completa

- **README.md** - Descripción general del proyecto
- **QUICKSTART.md** - Guía rápida de uso
- **http://localhost:8000/api/docs** - Documentación interactiva

## ✨ Características Implementadas

✅ Búsqueda semántica con embeddings
✅ Re-ranking con cross-encoders
✅ API REST completamente documentada
✅ Autenticación con API Keys
✅ Gestión de documentos (upload, delete, update)
✅ Estadísticas de colección
✅ Health checks
✅ Manejo de errores robusto
✅ Logging completo
✅ Validación de datos con Pydantic
✅ CORS configurado
✅ Scripts de utilidad

## 🎉 ¡Listo!

Tu SaaS de búsqueda semántica está completamente funcional.

Próximos pasos:

1. Sube tus propios documentos
2. Ajusta los modelos de IA si necesitas (más rápidos o más precisos)
3. Integra con tu aplicación frontend
4. Escala a producción

---

**¿Preguntas?** Consulta la documentación interactiva en `http://localhost:8000/api/docs`
