# Semantic Search SaaS - Configuration Guide

## Quick Start

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Copy environment template:**

```bash
cp .env.example .env
```

3. **Start the server:**

```bash
uvicorn app.main:app --reload
```

4. **Access API documentation:**

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Configuration Options

### Embedding Models

The system supports any model from the Sentence Transformers library.

**Lightweight (fast, 384-dim):**

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

**General purpose (768-dim):**

```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DIMENSION=768
```

**Multilingual (384-dim):**

```env
EMBEDDING_MODEL=sentence-transformers/xlm-r-base-en-fr-es
EMBEDDING_DIMENSION=768
```

**Domain-specific examples:**

```env
# Scientific papers
EMBEDDING_MODEL=sentence-transformers/allenai-specter

# Questions and answers
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Cross-Encoder Models (Re-ranking)

**Fast re-ranking:**

```env
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

**Better quality:**

```env
RERANK_MODEL=cross-encoder/ms-marco-TinyBERT-L-2-v2
```

**Multilingual:**

```env
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
```

## Database Setup

### Using Chroma (Default)

Already configured. Data is persisted in `./data/chroma_db`

### Migration to Other Backends

**PostgreSQL with pgvector:**

```python
# Install: pip install pgvector psycopg2-binary
from pgvector.sqlalchemy import Vector
# Implement VectorStore wrapper for pgvector
```

**Qdrant (Recommended for production):**

```bash
pip install qdrant-client
# Modify store.py to use QdrantClient
```

**Weaviate:**

```bash
pip install weaviate-client
# Implement integration
```

## API Key Management

Currently uses a simple header validation. For production:

```python
# In app/core/security.py
async def validate_api_key(x_api_key: str = Header(...)):
    # Implement database lookup
    user = await get_user_by_api_key(x_api_key)
    if not user:
        raise HTTPException(status_code=401)
    return user
```

### Generate API Keys

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Monitoring and Logging

### Enable Debug Logging

```env
DEBUG=true
```

### Log Files

Configure in `app/main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

## Performance Tuning

### For CPU-bound Systems

```env
# Use lighter models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RERANK_MODEL=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
TOP_K=5  # Reduce candidates before re-ranking
```

### For GPU Systems

```env
# Can use larger models
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
TOP_K=20  # More candidates, still fast with GPU
```

### Batch Processing

```bash
# Load 10,000+ documents efficiently
python scripts/load_json.py large_dataset.json
```

## Testing

Create `tests/test_api.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search():
    response = client.post("/api/v1/search/query", json={
        "query": "test query",
        "top_k": 5
    })
    assert response.status_code == 200
```

Run tests:

```bash
pytest tests/ -v
```

## Deployment

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t semantic-search .
docker run -p 8000:8000 -v $(pwd)/data:/app/data semantic-search
```

### Production Server (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Environment Variables

```bash
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
export CHROMA_PERSIST_DIRECTORY="/var/lib/semantic_search/db"
export DEBUG=false
```

## Scaling Considerations

### Single Server

- Up to ~100K documents
- Suitable for: Prototyping, small teams

### Multiple Servers with Load Balancer

- Shared Chroma database (NFS mount or cloud storage)
- Nginx or HAProxy load balancing
- Suitable for: Medium deployments

### Cloud Deployment

- Managed vector DB (e.g., Pinecone, Weaviate Cloud)
- Serverless compute (Lambda, Cloud Functions)
- Managed API Gateway
- Suitable for: Enterprise, high availability

### Caching Layer

Add Redis for popular searches:

```python
from redis import Redis
redis = Redis(host='localhost', port=6379)

@router.post("/api/v1/search/query")
async def search(query: SearchQuery):
    cache_key = f"search:{query.query}:{query.top_k}"
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... perform search
    redis.setex(cache_key, 3600, json.dumps(results))
```

## Security Checklist

- [ ] Change default API configuration
- [ ] Implement proper API key management
- [ ] Enable HTTPS in production
- [ ] Set up rate limiting
- [ ] Configure CORS appropriately
- [ ] Implement audit logging
- [ ] Use environment variables for secrets
- [ ] Validate all user inputs
- [ ] Set up regular backups
- [ ] Monitor for suspicious activity

## Support and Resources

- **Sentence Transformers**: https://www.sbert.net/
- **Chroma**: https://www.trychroma.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Cross-Encoders**: https://www.sbert.net/docs/usage/cross_encoders/
