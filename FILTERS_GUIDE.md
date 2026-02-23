# Guía de Filtros - Sistema de Búsqueda Semántica

## 📋 Resumen

El sistema ahora soporta **filtros flexibles** en las búsquedas. Puedes filtrar por cualquier campo que agregues en `metadata`, siempre que sea un tipo simple (string, number, boolean).

## 🔧 Cómo Funciona

### 1. Al Subir Documentos

Agrega campos en `metadata` que quieras usar para filtrar:

```json
{
  "documents": [
    {
      "id": "doc-001",
      "title": "Introducción a Machine Learning",
      "content": "El machine learning es...",
      "keywords": ["ml", "ai", "tutorial"],
      "metadata": {
        "category": "tutorial",
        "language": "es",
        "author": "Juan Pérez",
        "date": "2024-01-15",
        "department": "IT",
        "priority": "high",
        "version": "1.0"
      }
    },
    {
      "id": "doc-002",
      "title": "Deep Learning Avanzado",
      "content": "Las redes neuronales profundas...",
      "keywords": ["deep learning", "neural networks"],
      "metadata": {
        "category": "advanced",
        "language": "es",
        "author": "María García",
        "date": "2024-02-20",
        "department": "Research",
        "priority": "medium"
      }
    }
  ]
}
```

### 2. Al Buscar con Filtros

Usa el campo `filters` en tu búsqueda:

```json
{
  "query": "redes neuronales",
  "top_k": 10,
  "filters": {
    "category": "tutorial",
    "language": "es"
  }
}
```

**Resultado:** Solo encontrará documentos que:

1. Sean semánticamente relevantes a "redes neuronales"
2. Y tengan `category = "tutorial"`
3. Y tengan `language = "es"`

## 📊 Campos Filtrables Predefinidos

El sistema automáticamente indexa este campo mínimo si está en `metadata`:

- **`language`** - Código de idioma (es, en, fr) o lenguaje de programación (python, javascript, java)

**Nota:** Puedes agregar cualquier otro campo personalizado en `metadata` y será guardado completo en el documento. ChromaDB los indexará bajo demanda cuando los uses en un filtro.

## 🎯 Ejemplos de Uso

### Ejemplo 1: Filtrar por Idioma

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "authentication",
    "top_k": 5,
    "filters": {
      "language": "es"
    }
  }'
```

### Ejemplo 2: Filtrar por ID personalizado

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "best practices",
    "top_k": 10,
    "filters": {
      "id": "project-2024"
    }
  }'
```

### Ejemplo 3: Filtrar por campo personalizado

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "database configuration",
    "top_k": 20,
    "filters": {
      "language": "en",
      "custom_category": "devops"
    }
  }'
```

### Ejemplo 4: Sin Filtros (búsqueda normal)

```bash
curl -X POST "http://localhost:8000/api/v1/search/query" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "react hooks",
    "top_k": 5
  }'
```

## 🔑 Campos Personalizados

Puedes agregar **cualquier campo** en metadata (con prefijo "custom\_" recomendado para claridad):

```json
{
  "metadata": {
    "id": "my-doc",
    "language": "es",
    "custom_project": "API-2024",
    "custom_version": "1.0",
    "custom_status": "active",
    "custom_author": "Developer Name"
  }
}
```

Y luego filtrar por ellos:

```json
{
  "query": "authentication",
  "filters": {
    "custom_project": "API-2024",
    "custom_status": "active"
  }
}
```

**Nota importante:** Solo los campos `id` y `language` se indexan automáticamente. Para filtrar por otros campos personalizados, ChromaDB los indexará bajo demanda cuando los uses por primera vez.

## ⚠️ Limitaciones

### Tipos Soportados para Filtros

Solo se pueden filtrar campos con tipos simples:

- ✅ String: `"tutorial"`, `"es"`, `"Juan Pérez"`
- ✅ Number: `123`, `45.6`
- ✅ Boolean: `true`, `false`

### Tipos NO Soportados para Filtros

- ❌ Arrays/Listas: `["tag1", "tag2"]`
- ❌ Objetos anidados: `{"nested": {"field": "value"}}`
- ❌ Null: `null`

**Nota:** Estos tipos se guardan en el documento completo y se recuperan, pero NO se pueden usar para filtrar.

## 🎨 Casos de Uso

### Documentación Multiidioma

```json
{
  "metadata": {
    "id": "doc-ml-intro",
    "language": "es"
  }
}
```

### Repositorio de Código

```json
{
  "metadata": {
    "id": "tutorial-python-001",
    "language": "python",
    "custom_category": "backend",
    "custom_level": "intermediate"
  }
}
```

### Content Management

```json
{
  "metadata": {
    "id": "article-2024-02",
    "language": "en",
    "custom_author": "John Doe",
    "custom_status": "published"
  }
}
```

### API Logs/Traces

```json
{
  "metadata": {
    "id": "trace-auth-service",
    "language": "json",
    "custom_environment": "prod",
    "custom_severity": "error"
  }
}
```

## 💡 Ventajas

1. **Flexibilidad** - Define tus propios campos sin modificar código
2. **Precisión** - Combina búsqueda semántica + filtros exactos
3. **Performance** - Los filtros están indexados en ChromaDB
4. **Escalabilidad** - Cada documento puede tener diferentes campos

## 🚀 Recomendaciones

1. **Planifica tus campos** - Define qué campos necesitarás filtrar
2. **Usa nombres consistentes** - `category` siempre en minúscula
3. **Tipos simples** - Usa strings para campos complejos (ej: date como string)
4. **Documenta tus campos** - Mantén una lista de campos que usas
