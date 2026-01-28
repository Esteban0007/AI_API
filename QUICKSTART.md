# Semantic Search SaaS - Quick Start Guide

## 1. Instalación Rápida (5 minutos)

```bash
# Clonar/descargar el proyecto
cd /ruta/a/API_IA

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## 2. Crear Datos de Ejemplo

```bash
# Generar documentos de ejemplo
python scripts/create_sample_data.py

# Cargar en la base de datos
python scripts/load_json.py data/sample_documents.json
```

## 3. Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará en: `http://localhost:8000`

## 4. Probar con curl

### Búsqueda Semántica

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cómo funcionan las redes neuronales?",
    "top_k": 3
  }'
```

### Cargar Documentos

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc-test-001",
        "title": "Mi Documento",
        "content": "Este es el contenido del documento que quiero buscar",
        "metadata": {
          "category": "test",
          "language": "es"
        }
      }
    ]
  }'
```

### Ver Estadísticas

```bash
curl "http://localhost:8000/api/v1/documents/stats"
```

### Health Check

```bash
curl "http://localhost:8000/api/v1/search/health"
```

## 5. Interfaz Web

Accede a la documentación interactiva:

**Swagger UI** → http://localhost:8000/api/docs

- Prueba endpoints directamente desde la UI
- Visualiza esquemas de request/response
- Genera código de ejemplo

**ReDoc** → http://localhost:8000/api/redoc

- Documentación estilo libro
- Mejor para leer offline

## 6. Ejemplos de Búsqueda

### Ejemplo 1: Búsqueda Simple

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/search/query",
    json={
        "query": "Visión por computadora",
        "top_k": 3
    }
)

for result in response.json()["results"]:
    print(f"📄 {result['title']}")
    print(f"   Score: {result['score']:.2f}")
    print()
```

### Ejemplo 2: Con Más Opciones

```python
response = requests.post(
    "http://localhost:8000/api/v1/search/query",
    json={
        "query": "algoritmos de aprendizaje",
        "top_k": 5,
        "include_content": True,
        "filters": {"language": "es"}
    }
)

results = response.json()
print(f"Encontrados: {results['total_results']} resultados")
print(f"Tiempo: {results['execution_time_ms']:.2f}ms")
```

### Ejemplo 3: Cargar Documentos Personalizados

```python
import json

# Crear documentos
docs = {
    "documents": [
        {
            "id": "mi-doc-1",
            "title": "Título de mi artículo",
            "content": "Este es mi contenido personalizado...",
            "keywords": ["palabra-clave-1", "palabra-clave-2"],
            "metadata": {
                "category": "mi-categoría",
                "language": "es",
                "source": "https://mi-sitio.com"
            }
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/documents/upload",
    json=docs
)

print(response.json())
```

## 7. Estructura de Respuesta de Búsqueda

```json
{
  "query": "¿Cómo funciona?",
  "total_results": 3,
  "results": [
    {
      "id": "doc-001",
      "title": "Título del Documento",
      "score": 0.95,
      "content": "El contenido del documento...",
      "metadata": {
        "category": "tutorial",
        "language": "es",
        "title": "Título del Documento"
      }
    }
  ],
  "execution_time_ms": 125.5
}
```

**Campo `score`**: Relevancia (0.0 a 1.0)

- 0.9+ : Muy relevante
- 0.7-0.9 : Relevante
- 0.5-0.7 : Moderadamente relevante
- <0.5 : Poco relevante

## 8. Configuración Rápida

### Cambiar Modelo de Embeddings

Editar `app/core/config.py`:

```python
# Opción 1: Rápido (recomendado para CPU)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Opción 2: Más preciso
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Opción 3: Multilingüe
EMBEDDING_MODEL = "sentence-transformers/distiluse-base-multilingual-cased-v2"
```

### Ajustar Parámetros de Búsqueda

```python
TOP_K = 10      # Candidatos antes de re-ranking
RERANK_TOP_K = 5  # Resultados finales a devolver
```

## 9. Troubleshooting

### ❌ Error: "No module named 'sentence_transformers'"

```bash
pip install sentence-transformers
```

### ❌ Error: "Chroma database locked"

```bash
rm -rf data/chroma_db
# El sistema recrearaá la base de datos automáticamente
```

### ❌ Búsquedas lentas

1. Verificar si se está usando GPU:

```python
import torch
print(torch.cuda.is_available())  # True = GPU disponible
```

2. Si no hay GPU, usar modelo más ligero en config

### ❌ Resultados poco relevantes

1. Aumentar `TOP_K` antes de re-ranking
2. Cambiar a modelo más preciso
3. Agregar más documentos
4. Mejorar el contenido de los documentos

## 10. Próximos Pasos

1. **Integración en tu app**:

   - Usar como API desde tu frontend/backend
   - Implementar cache de resultados populares

2. **Escalar**:

   - Cambiar a Qdrant o Weaviate para más documentos
   - Agregar autenticación más robusta
   - Implementar rate limiting

3. **Personalizar**:

   - Entrenar modelos propios
   - Añadir análisis de sentimiento
   - Integrar con bases de datos externas

4. **Producción**:
   - Dockerizar la aplicación
   - Desplegar en cloud (AWS, GCP, Azure)
   - Configurar monitoreo y logs
   - Implementar CI/CD

## 11. Recursos

- 📚 **Documentación Completa**: Ver `README.md`
- 🚀 **Guía de Deployment**: Ver `DEPLOYMENT.md`
- 🔧 **Configuración Avanzada**: Ver `app/core/config.py`
- 💡 **Ejemplos**: Ver `scripts/` y `data/sample_documents.json`

---

¿Necesitas ayuda? Revisa la documentación interactiva en `/api/docs`
