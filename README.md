# 🔍 ReadyAPI - Semantic Search Platform

> **Intelligent Text Search Through Meaning, Not Keywords**  
> A production-ready semantic search engine powered by modern embeddings and intelligent ranking.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Deployed on VPS](https://img.shields.io/badge/Deployed-194.164.207.6-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🌐 **Live**: [https://readyapi.net](https://readyapi.net) | 📚 **Docs**: [https://api.readyapi.net/api/docs](https://api.readyapi.net/api/docs) | 🎮 **Demos**: [https://readyapi.net/demos](https://readyapi.net/demos)

---

## 📖 Table of Contents

- [What is ReadyAPI?](#what-is-readyapi)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Performance](#performance)
- [Project Structure](#project-structure)

---

## 🎯 What is ReadyAPI?

**ReadyAPI** is a semantic search platform that understands the **meaning** behind queries rather than just matching keywords.

### Traditional Search vs Semantic Search

```
Query: "robot wants to become human"

❌ Traditional Search:
   → Only returns results with exact words "robot", "wants", "human"
   → Misses: "android dreams of humanity" or "machine consciousness"

✅ ReadyAPI (Semantic):
   → Understands the concept of consciousness/humanity in machines
   → Returns: Blade Runner, A.I., Ex Machina, even in other languages
```

### When You Need ReadyAPI

- 📚 **Documentation Systems** - Find answers by topic, not exact phrases
- 🛍️ **E-commerce** - Search products by intent ("comfortable shoes for running")
- 📰 **Content Platforms** - Discover related articles semantically
- 💼 **Internal Knowledge Bases** - Search company docs across languages
- 🌍 **Multilingual Apps** - Search works in Spanish, English, Italian, etc.

---

## ✨ Key Features

### 🧠 Smart Embeddings

- **Snowflake Arctic Embeddings (768-dimensional)** - State-of-the-art semantic representation
- **Multi-language support** - Search works across 40+ languages seamlessly
- **Efficient encoding** - Fast embedding generation without GPU dependency

### 🎯 Advanced Ranking

- **Vector similarity search** - Dense retrieval via embeddings
- **Hybrid ranking** - Combines semantic + keyword matching (BM25)
- **Result fusion** - Reciprocal Rank Fusion for best of both worlds
- **Configurable relevance** - Tune search behavior per use case

### 🚀 Production Ready

- **RESTful API** - Simple HTTP endpoints for integration
- **API Key authentication** - Secure access control with per-user isolation
- **Rate limiting** - Protect against abuse
- **CORS enabled** - Works with web frontends
- **4+ concurrent workers** - Handle multiple simultaneous requests
- **Deployed & live** - Running on 194.164.207.6 with real data

### 🎨 Live Interactive Demos

- **Movie Search** - Search 2000+ TMDB movies semantically
- **Interactive Spaceship** - Visual demo with 7 systems (charge, fly, stealth, attack, shield, scan, repair)
- **ReadyAPI Documentation** - Search through features and guides
- **Multi-language support** - Try searches in Spanish, Italian, English

### 📊 Admin Tools

- **User management** - Create users and API keys via CLI
- **Search statistics** - Monitor collection size and performance
- **Index management** - Rebuild or modify search indexes
- **Batch operations** - Upload 100+ documents at once

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Client Application (Web/Mobile/CLI)                     │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         │
        ┌────────────────▼────────────────┐
        │ nginx Reverse Proxy              │
        │ (SSL/TLS, Rate Limiting)        │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │ Gunicorn + Uvicorn Workers      │
        │ (4 workers × 500MB each)        │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────┐
        │ FastAPI Application Layer                         │
        ├───────────────────────────────────────────────────┤
        │ ├─ Authentication & Authorization                 │
        │ ├─ Document Upload Pipeline                       │
        │ ├─ Search Orchestration                           │
        │ └─ Response Formatting                            │
        └────────────────┬──────────────────────────────────┘
                         │
        ┌────────────────┴──────────────────────────────────┐
        │ Search & Storage Layer                            │
        ├───────────────────────────────────────────────────┤
        │ ├─ Embedding Engine (Snowflake Arctic)            │
        │ ├─ Vector Store (Chroma DB - 137MB)               │
        │ └─ Ranking Engine (Hybrid + RRF)                  │
        └────────────────┬──────────────────────────────────┘
                         │
        ┌────────────────▼──────────────────────────────────┐
        │ Database Layer                                    │
        ├───────────────────────────────────────────────────┤
        │ ├─ Users & API Keys (SQLite)                      │
        │ ├─ Collections & Metadata                         │
        │ └─ Search Logs & Statistics                       │
        └───────────────────────────────────────────────────┘
```

### Data Flow

```
User Query
    ↓
1. Validate API Key & Rate Limit
    ↓
2. Embed Query (Snowflake Arctic - 768D)
    ↓
3. Vector Search in Chroma DB
    ↓
4. Apply Hybrid Ranking (BM25 + Vector)
    ↓
5. Rank with Reciprocal Rank Fusion
    ↓
6. Return Top-K Results with Scores & Timing
```

---

## 🛠️ Tech Stack

| Component        | Technology                               | Version | Purpose                           |
| ---------------- | ---------------------------------------- | ------- | --------------------------------- |
| **Backend**      | FastAPI                                  | 0.104+  | HTTP API server                   |
| **Server**       | Uvicorn                                  | 0.24+   | ASGI application server           |
| **Embeddings**   | Sentence Transformers (Snowflake Arctic) | 3.0+    | Convert text → 768D vectors       |
| **Vector DB**    | Chroma DB                                | 0.4+    | Store & search embeddings (137MB) |
| **Database**     | SQLite / PostgreSQL                      | Latest  | Users, API keys, metadata         |
| **Frontend**     | Jinja2 + HTML/CSS/JS                     | Latest  | Web interface & demos             |
| **ML Framework** | PyTorch                                  | 2.1+    | Embedding model inference         |
| **Search Utils** | scikit-learn                             | 1.3+    | BM25 keyword indexing             |
| **Inference**    | ONNX Runtime                             | 1.17+   | Optimized inference               |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- 4GB RAM (8GB+ recommended for production)
- Internet connection (for first-time embedding download ~380MB)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/readyapi.git
cd readyapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Create your first user
python scripts/create_user.py \
  --email user@example.com \
  --name "John Doe" \
  --plan free
```

### Run Locally

```bash
# Start development server (auto-reload)
python scripts/run_server.py

# Server runs at http://localhost:8000
# API docs: http://localhost:8000/api/docs
# Interactive demos: http://localhost:8000/demos
```

---

## 📡 API Endpoints

### Upload Documents

**POST** `/api/v1/documents/upload`

Upload documents to index them for searching.

```bash
curl -X POST https://api.readyapi.net/api/v1/documents/upload \
  -H "x-api-key: rapi_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc-1",
        "title": "Understanding Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence..."
      },
      {
        "id": "doc-2",
        "title": "Deep Learning Basics",
        "content": "Deep learning uses neural networks with multiple layers..."
      }
    ]
  }'
```

**Response:** `{ "documents_added": 2, "documents_failed": 0 }`

### Search Documents

**POST** `/api/v1/documents/search`

Search through your indexed documents semantically.

```bash
curl -X POST https://api.readyapi.net/api/v1/documents/search \
  -H "x-api-key: rapi_YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how do neural networks learn",
    "top_k": 5
  }'
```

**Response:**

```json
{
  "results": [
    {
      "id": "doc-2",
      "title": "Deep Learning Basics",
      "score": 0.89,
      "content": "Deep learning uses neural networks..."
    }
  ],
  "timing_ms": 45
}
```

### Get Statistics

**GET** `/api/v1/documents/stats`

Check how many documents are indexed.

```bash
curl -H "x-api-key: rapi_YOUR_API_KEY" \
  https://api.readyapi.net/api/v1/documents/stats
```

**Response:**

```json
{
  "collection_name": "documents",
  "document_count": 1250,
  "embedding_dimension": 768,
  "storage_mb": 45.2
}
```

### List All Documents

**GET** `/api/v1/documents/all`

Retrieve all indexed documents with metadata.

```bash
curl -H "x-api-key: rapi_YOUR_API_KEY" \
  https://api.readyapi.net/api/v1/documents/all
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Database
DATABASE_URL=sqlite:///./data/app.db
# Or PostgreSQL: postgresql://user:password@localhost/readyapi

# API
API_TITLE=ReadyAPI
API_VERSION=1.0.0
API_DESCRIPTION=Semantic Search Platform

# Security
SECRET_KEY=your-secret-key-change-this
ALLOWED_ORIGINS=["http://localhost:3000", "https://example.com"]

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DEVICE=cpu  # or 'cuda' for GPU

# Search
DEFAULT_TOP_K=5
MAX_DOCUMENT_SIZE=10000
```

---

## 💻 Development

### Project Structure

```
readyapi/
├── app/
│   ├── main.py              # FastAPI application factory
│   ├── api/
│   │   ├── __init__.py
│   │   ├── web.py           # Web pages & demos (GET routes)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── documents.py # POST /upload, /search endpoints
│   │       ├── search.py    # Search query handling
│   │       └── users.py     # User management endpoints
│   ├── core/
│   │   ├── config.py        # Environment & settings
│   │   ├── security.py      # API key auth & encryption
│   │   └── email.py         # Email notifications
│   ├── db/
│   │   ├── session.py       # SQLAlchemy session management
│   │   ├── connection.py    # DB connection setup
│   │   └── users.py         # User table models
│   ├── engine/
│   │   ├── embedder.py      # Snowflake Arctic embeddings
│   │   ├── searcher.py      # Search & ranking logic
│   │   └── store.py         # Chroma DB interface
│   ├── models/
│   │   ├── user.py          # User SQLAlchemy model
│   │   ├── document.py      # Document model
│   │   └── search.py        # Search result model
│   ├── static/              # CSS, JavaScript files
│   └── templates/           # Jinja2 HTML (index, demos, 404)
├── scripts/
│   ├── run_server.py        # Dev server (uvicorn)
│   ├── run_server_https.py  # Dev server with SSL
│   ├── init_db.py           # Initialize database & tables
│   ├── create_user.py       # Admin: create user + API key
│   ├── list_users.py        # Admin: list all users
│   ├── load_json.py         # Load documents from JSON
│   ├── load_documents.py    # Advanced document loading
│   ├── rebuild_index.py     # Rebuild vector embeddings
│   ├── deploy.sh            # Deployment automation script
│   ├── cleanup_old_consents.py      # (deprecated - GDPR)
│   └── view_consent_records.py      # (deprecated - GDPR)
├── tests/
│   ├── test_example.py           # Basic API test
│   ├── test_upload_10k.py        # Bulk upload test
│   ├── test_movies_ndcg.py       # Search quality test
│   └── test_1000_searches.py     # Performance test
├── data/
│   ├── dataset_movies_en_clean.json          # 2000 TMDB movies
│   ├── movies_dataset.json                   # Complete movies dataset
│   ├── readyapi_instructions.json            # Platform documentation
│   ├── payload_definitions.json              # API example payload
│   ├── data_demo_spaceship.json              # Spaceship demo data
│   └── data_demo_readyapi_instructions.json  # Demo instructions
├── deploy/
│   ├── nginx.conf           # Production reverse proxy config
│   ├── docker-compose.yml   # Docker services
│   └── DEPLOYMENT_READYAPI.md
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

### Running Tests

ReadyAPI includes comprehensive test suites to verify functionality and performance:

**Test Files:**

- **`test_example.py`** - Basic smoke test (embedder, vector store, search engine)

  ```bash
  python tests/test_example.py
  ```

  Tests: Embedding generation, document storage, query search

- **`test_upload_10k.py`** - Bulk upload stress test (10,000 documents)

  ```bash
  python tests/test_upload_10k.py
  ```

  Tests: Large batch uploads, memory handling, response times

- **`test_movies_ndcg.py`** - Search quality test (nDCG@5 ranking)

  ```bash
  python tests/test_movies_ndcg.py
  ```

  Tests: Semantic ranking quality, relevance scores, expected results

- **`test_1000_searches.py`** - Load test (1000 concurrent searches)
  ```bash
  python tests/test_1000_searches.py
  ```
  Tests: Throughput, latency under load, error handling

**Run All Tests:**

```bash
# Against local development server
python -m pytest tests/ -v

# Against production server (requires API key)
export API_KEY=rapi_YOUR_KEY
python tests/test_upload_10k.py
python tests/test_movies_ndcg.py
```

**Performance Targets:**

- Search latency: < 150ms (p95)
- Embedding speed: 50-100 docs/sec
- nDCG@5 score: > 0.80 (ranking quality)
- Throughput: 10-15 req/sec per worker

### Code Style

```bash
# Format code with Black
black app/ scripts/

# Lint with Flake8
flake8 app/ scripts/

# Type checking with mypy
mypy app/
```

---

## 🚀 Deployment

### Current Production Setup

**Live server**: 194.164.207.6 (readyapi.net)

- **OS**: Linux
- **Web Server**: nginx (SSL/TLS)
- **App Server**: Gunicorn + Uvicorn (4 workers)
- **Database**: PostgreSQL
- **Storage**: 137MB for vector data
- **Uptime**: Monitored with health checks

### Deploy to Your Server

```bash
# SSH into server
ssh user@your-server.com

# Clone repository
git clone https://github.com/yourusername/readyapi.git
cd readyapi

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Run with Gunicorn + Uvicorn (production)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Using Docker

```bash
# Build image
docker build -t readyapi:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=your-secret \
  readyapi:latest
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.readyapi.net;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.readyapi.net;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/readyapi.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/readyapi.net/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

---

## 📊 Performance

### Benchmark Results (Real Data)

| Metric               | Value            | Details                         |
| -------------------- | ---------------- | ------------------------------- |
| **Storage**          | 137MB            | Vector database + metadata      |
| **Embedding Speed**  | ~50-100 docs/sec | CPU: Intel standard, 4GB RAM    |
| **Search Latency**   | 45-150ms         | P50 latency for 2000 documents  |
| **Query Throughput** | ~10-15 req/sec   | Per worker (4 workers deployed) |
| **Model Size**       | ~380MB           | Snowflake Arctic embeddings     |
| **Memory/Worker**    | ~500MB           | Per uvicorn process             |

### Real Deployment Stats

- **Live Instance**: readyapi.net (194.164.207.6)
- **Database Size**: 137MB (Chroma vector store)
- **Concurrent Workers**: 4
- **Uptime**: Continuous monitoring active

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Support & Questions

- 📖 **Documentation**: [https://readyapi.net/docs](https://readyapi.net/docs)
- 🎮 **Live Demos**: [https://readyapi.net/demos](https://readyapi.net/demos)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/readyapi/issues)
- 📧 **Email**: support@readyapi.net

---

## 🙏 Acknowledgments

- **Snowflake** for Arctic embeddings model
- **Chroma** for excellent vector database
- **FastAPI** community for fantastic framework
- **Hugging Face** for transformers library
- Contributors and users of ReadyAPI

---

**Made with ❤️ for semantic understanding**

Last Updated: April 2026 | Version: 1.0.0
