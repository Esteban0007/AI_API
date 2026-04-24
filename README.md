# 🔍 ReadyAPI: A Semantic Search Platform


**Author**: Esteban Bardolet  
**Date**: April 2026  
**Live Demo**: [https://readyapi.net](https://readyapi.net)

---

## 📖 Table of Contents

- [Problem Statement](#problem-statement)
- [Project Motivation](#project-motivation)
- [Proposed Solution](#proposed-solution)
- [Architecture & Design](#architecture--design)
- [Implementation Details](#implementation-details)
- [Key Features Developed](#key-features-developed)
- [Technology Stack](#technology-stack)
- [Results & Performance](#results--performance)
- [Challenges & Solutions](#challenges--solutions)
- [Conclusions](#conclusions)
- [Project Structure](#project-structure)

---

## 🎯 Problem Statement

**The Challenge**: Traditional search engines use keyword matching, which fails when:
- Users search for concepts, not exact phrases ("sustainable running shoes" ≠ "eco-friendly athletic footwear")
- Content is in multiple languages (search in English, results in Spanish/Italian)
- Documents are poorly structured or lack proper indexing
- Users don't know the exact terminology

**Current Market Gap**: Most semantic search solutions are either:
1. **Cloud-only** (expensive, vendor lock-in, privacy concerns)
2. **Over-engineered** (overkill for small/medium use cases)
3. **Closed-source** (can't customize or understand the system)
4. **Difficult to deploy** (complex setup, high infrastructure costs)

---

## 💡 Project Motivation

This thesis explores building a **self-hosted, accessible semantic search platform** that:
- Understands **meaning** instead of just keywords
- Works **across languages** seamlessly
- Can be deployed **on modest hardware** (4GB RAM)
- Provides **production-grade performance**
- Easy Json i Json out not expertise needed

The goal is to make semantic search technology easy, making it accessible to developers and organizations without requiring expensive cloud services or complex infrastructure.

---

## ✅ Proposed Solution

**ReadyAPI** is a self-hosted semantic search platform that combines:

### 1. **Modern Embeddings**
- Uses **Snowflake Arctic** (state-of-the-art 768D embeddings)
- Supports 40+ languages natively
- Runs on CPU without requiring GPU

### 2. **Hybrid Ranking Strategy**
- **Dense retrieval** via vector embeddings (semantic understanding)
- **Sparse retrieval** via BM25 (exact keyword matching)
- **Result fusion** via Reciprocal Rank Fusion (combines both signals)

### 3. **Production-Ready Architecture**
- RESTful HTTP API for easy integration
- Multi-worker concurrency (handles parallel requests)
- Secure API key authentication
- Real-time search statistics

### 4. **Practical Demonstrations**
- Live interactive movie search (2000+ TMDB movies)
- Visual spaceship systems demo (7 interactive systems)
- ReadyAPI documentation search
- Multi-language support showcase

---

## 🏗️ Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Client Applications (Web/Mobile/API)                    │
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS
                         ▼
        ┌────────────────────────────────────────┐
        │ Reverse Proxy (nginx)                  │
        │ - SSL/TLS encryption                   │
        │ - Rate limiting                        │
        │ - Load balancing                       │
        └────────────────┬─────────────────────────┘
                         │
        ┌────────────────▼──────────────────────┐
        │ Application Layer (FastAPI)            │
        ├─────────────────────────────────────────┤
        │ • API Key Authentication                │
        │ • Request Validation                    │
        │ • Business Logic Orchestration          │
        │ • Response Formatting                   │
        └────────────────┬──────────────────────┘
                         │
        ┌────────────────▼──────────────────────────┐
        │ Search & ML Layer                         │
        ├───────────────────────────────────────────┤
        │ 1. Embedding Engine (Snowflake Arctic)    │
        │    └─ Converts text to 768D vectors      │
        │ 2. Vector Store (Chroma DB)              │
        │    └─ Stores and retrieves embeddings    │
        │ 3. Ranking Engine                        │
        │    └─ BM25 + Vector + RRF fusion        │
        └────────────────┬──────────────────────────┘
                         │
        ┌────────────────▼──────────────────────┐
        │ Data Layer (Databases)                │
        ├─────────────────────────────────────────┤
        │ • SQLite/PostgreSQL (Users, API Keys) │
        │ • Chroma DB (Vector Storage)           │
        │ • Metadata & Collections               │
        └───────────────────────────────────────┘
```

### Search Pipeline (Step-by-Step)

```
User Query: "How do neural networks learn?"
    │
    ├─ Step 1: Validate API Key & Rate Limit
    │   ✓ Verify credentials
    │   ✓ Check request quota
    │
    ├─ Step 2: Embed Query
    │   ✓ Use Snowflake Arctic model
    │   ✓ Generate 768-dimensional vector
    │
    ├─ Step 3: Retrieve Candidates
    │   ✓ Vector similarity search (dense)
    │   ✓ BM25 keyword search (sparse)
    │   ✓ Get top 100 candidates from each
    │
    ├─ Step 4: Rank Results
    │   ✓ Apply Reciprocal Rank Fusion
    │   ✓ Combine semantic + keyword signals
    │   ✓ Sort by combined score
    │
    └─ Step 5: Return Top-K Results
        ✓ Return top 5 results with scores
        ✓ Include timing information
        ✓ Return in JSON format
```

### Design Decisions & Rationale

| Decision | Choice | Why |
|----------|--------|-----|
| **Embedding Model** | Snowflake Arctic (768D) | State-of-the-art, multilingual, accessible size |
| **Vector Database** | Chroma DB | Lightweight, easy to deploy, sufficient for thesis scope |
| **Search Strategy** | Hybrid (Dense + Sparse) | Combines semantic understanding with exact matching |
| **Ranking Method** | Reciprocal Rank Fusion | Proven effective at combining heterogeneous signals |
| **Backend Framework** | FastAPI | Modern, performant, excellent documentation |
| **Server** | Uvicorn + Gunicorn | Production-grade ASGI with process management |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Scales from local to production |
| **Deployment** | Docker + nginx | Reproducible, scalable, industry-standard |

---

## 🔧 Implementation Details

### Phase 1: Core Search Engine (Weeks 1-4)
**Objective**: Build basic semantic search functionality

- [x] Set up FastAPI project structure
- [x] Implement document upload endpoint
- [x] Integrate Snowflake Arctic embeddings
- [x] Build vector store with Chroma DB
- [x] Implement basic search endpoint
- [x] Add search result ranking

**Key Challenge**: First embedding pass took 15 minutes for 2000 documents.  
**Solution**: Implemented batch processing and caching.

### Phase 2: Ranking & Search Quality (Weeks 5-7)
**Objective**: Improve search result quality through hybrid ranking

- [x] Implement BM25 keyword indexing
- [x] Create Reciprocal Rank Fusion algorithm
- [x] Test ranking quality (nDCG@5 metric)
- [x] Optimize for relevance

**Key Challenge**: Balancing semantic vs keyword relevance.  
**Solution**: Tuned RRF weights through empirical testing.

### Phase 3: Production Architecture (Weeks 8-10)
**Objective**: Build production-grade deployment

- [x] Add API key authentication system
- [x] Implement rate limiting
- [x] Set up multi-worker architecture
- [x] Configure nginx reverse proxy
- [x] Enable SSL/TLS encryption
- [x] Deploy to VPS (194.164.207.6)

**Key Challenge**: Memory constraints on VPS (2GB available).  
**Solution**: Implemented INT8 quantization, batch limiting, garbage collection.

### Phase 4: Interactive Demos & UI (Weeks 11-13)
**Objective**: Create engaging demonstrations of capabilities

- [x] Build movie search demo (2000 TMDB movies)
- [x] Create interactive spaceship systems demo
- [x] Add ReadyAPI documentation search
- [x] Implement multi-language support display
- [x] Create professional landing page

**Key Challenge**: Real-time interactivity with semantic search latency.  
**Solution**: Optimized frontend, added progress indicators, 45-150ms latency achievable.

---

## ✨ Key Features Developed

### 1. RESTful API (`/api/v1/documents`)
- **Upload** documents for indexing
- **Search** across indexed documents
- **Get statistics** about collections
- **List all** documents with metadata

### 2. Authentication & Security
- **API Key system** for user identification
- **Per-user data isolation** (multi-tenant architecture)
- **Rate limiting** to prevent abuse
- **CORS support** for web integrations

### 3. Hybrid Search Engine
- **Vector search** using embeddings
- **Keyword search** using BM25
- **Result fusion** via Reciprocal Rank Fusion
- **Configurable ranking** parameters

### 4. Multi-Language Support
- Seamless search across 40+ languages
- Cross-lingual retrieval (search in English, results in Spanish)
- Language detection and handling

### 5. Admin Tools
- Create users and API keys via CLI
- Monitor collection statistics
- View search performance metrics
- Rebuild indexes when needed

---

## 🛠️ Technology Stack

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **API Server** | FastAPI | 0.104+ | Modern, async-first, excellent for ML workloads |
| **ASGI Server** | Uvicorn | 0.24+ | Production-grade Python ASGI server |
| **Process Manager** | Gunicorn | Latest | Proven stability, multi-worker support |
| **Embeddings** | Sentence Transformers + Snowflake Arctic | 3.0+ | SOTA model, multilingual, accessible |
| **Vector DB** | Chroma DB | 0.4+ | Lightweight, embedded option, excellent for thesis scale |
| **Keyword Search** | scikit-learn (BM25) | 1.3+ | Reliable, well-tested ranking algorithm |
| **ML Framework** | PyTorch | 2.1+ | Industry standard, excellent performance |
| **Inference** | ONNX Runtime | 1.17+ | Hardware acceleration, optimized inference |
| **Web Server** | nginx | Latest | Reverse proxy, SSL/TLS, rate limiting |
| **Database** | PostgreSQL | 13+ | Production database, ACID compliance |
| **Containerization** | Docker | Latest | Reproducible, scalable deployment |
| **ORM** | SQLAlchemy | 2.0+ | Flexible, database-agnostic |
| **Frontend** | Jinja2 + HTML/CSS/JS | Latest | Server-side rendering, minimal dependencies |

---

## 📊 Results & Performance

### Benchmark Results (Real Production Data)

| Metric | Result | Context |
|--------|--------|---------|
| **Storage Efficiency** | 137MB | For 2000 TMDB movie documents + metadata |
| **Embedding Speed** | 50-100 docs/sec | CPU-only, 4GB RAM system |
| **Search Latency (P50)** | 45ms | Typical response time |
| **Search Latency (P95)** | 150ms | Worst case, includes network |
| **Query Throughput** | 10-15 req/sec | Per worker, 4 workers deployed |
| **Model Size** | 380MB | Snowflake Arctic embeddings |
| **Memory per Worker** | ~500MB | Uvicorn process overhead |
| **Ranking Quality (nDCG@5)** | 0.82 | Movie queries with human judgments |

### Deployment Stats

- **Live Instance**: readyapi.net (194.164.207.6)
- **Concurrent Users**: 4 workers handling ~50 concurrent requests
- **Uptime**: >99.9% with health checks
- **Database**: 137MB Chroma DB + PostgreSQL for users
- **Latency SLA**: <200ms for 99% of requests

---

## 🔥 Challenges & Solutions

### Challenge 1: Memory Constraints
**Problem**: VPS only had 2GB available RAM, embedding model needs 400MB+

**Solution**:
- Used INT8 quantization (75% memory reduction)
- Implemented batch size limiting (max 100 docs/batch)
- Added automatic garbage collection
- Optimized model loading

**Result**: System runs stably with <500MB per worker

---

### Challenge 2: Search Quality vs Speed Trade-off
**Problem**: Hybrid search was slow (dense + sparse + fusion = 500ms+)

**Solution**:
- Implemented parallel search (async operations)
- Optimized BM25 index structure
- Reduced candidate set size (top 100 instead of 1000)
- Cached frequent queries

**Result**: 45-150ms latency without sacrificing quality

---

### Challenge 3: Multi-language Support
**Problem**: Different languages have different tokenization, stemming needs

**Solution**:
- Used Snowflake Arctic (inherently multilingual)
- Implemented language-agnostic BM25 variant
- Added Unicode-aware tokenization

**Result**: Seamless cross-lingual search

---

### Challenge 4: Ranking Quality Evaluation
**Problem**: How to measure if semantic results are actually good?

**Solution**:
- Used nDCG@5 metric (Normalized Discounted Cumulative Gain)
- Created manual relevance judgments for movie queries
- Benchmarked against baseline (keyword-only search)

**Result**: Achieved 0.82 nDCG@5, 23% improvement over keyword-only

---

## 📈 Evaluation Methodology

### Metrics Used

1. **Ranking Quality (nDCG@5)**
   - Measures how well top 5 results match user expectations
   - Target: > 0.80 (achieved: 0.82)

2. **Latency (Response Time)**
   - P50: 45ms (typical)
   - P95: 150ms (worst case)
   - Goal: < 200ms for user experience

3. **Throughput (Requests/sec)**
   - Achieved: 10-15 req/sec per worker
   - Sufficient for thesis demonstration

4. **Storage Efficiency**
   - 137MB for 2000 documents
   - ~68KB per document (competitive)

### Test Suites

1. **test_example.py**: Basic functionality (embeddings, storage, search)
2. **test_upload_10k.py**: Stress test (10,000 document upload)
3. **test_movies_ndcg.py**: Ranking quality test (human judgments)
4. **test_1000_searches.py**: Load test (1000 concurrent searches)

---

## 🎓 Conclusions

### What Was Achieved

1. ✅ Built a fully functional semantic search platform from scratch
2. ✅ Demonstrated that self-hosted semantic search is feasible
3. ✅ Achieved competitive performance (0.82 nDCG@5)
4. ✅ Deployed to production with 99.9% uptime
5. ✅ Created interactive, educational demonstrations
6. ✅ Built scalable, multi-tenant architecture

### Key Insights

- **Hybrid search works**: Combining semantic + keyword matching outperforms either alone
- **Accessible to SMBs**: Can run on modest hardware (4GB RAM)
- **Trade-offs matter**: Balancing speed, quality, and cost is crucial
- **User experience**: Fast latency and clear results matter more than raw ranking accuracy

### Limitations & Future Work

**Current Limitations**:
- Single-language queries (but multilingual results possible)
- Fixed embedding model (not fine-tuned for specific domains)
- Synchronous document uploads (no streaming)
- No real-time index updates

**Future Improvements**:
- [ ] Fine-tune embeddings for specific domains (e-commerce, documentation, etc.)
- [ ] Implement real-time indexing with streaming uploads
- [ ] Add query expansion (synonyms, related concepts)
- [ ] Build admin dashboard for monitoring
- [ ] Support custom ranking models
- [ ] Add federated search across multiple collections

---

## 📁 Project Structure

### Directory Organization

```
readyapi/
├── app/                          # Main application
│   ├── main.py                  # FastAPI app factory
│   ├── api/
│   │   ├── web.py              # Web pages (demos, landing)
│   │   └── v1/documents.py      # API endpoints
│   ├── core/
│   │   ├── config.py           # Configuration management
│   │   └── security.py         # Authentication/API keys
│   ├── engine/
│   │   ├── embedder.py        # Embedding generation
│   │   ├── searcher.py        # Search logic & ranking
│   │   └── store.py           # Vector store interface
│   ├── models/                 # Database models
│   └── templates/              # HTML/UI
├── scripts/
│   ├── run_server.py          # Development server
│   ├── init_db.py             # Database initialization
│   ├── create_user.py         # User management
│   └── deploy.sh              # Deployment automation
├── tests/
│   ├── test_example.py        # Smoke tests
│   ├── test_upload_10k.py     # Stress tests
│   ├── test_movies_ndcg.py    # Quality tests
│   └── test_1000_searches.py  # Load tests
├── data/
│   ├── dataset_movies_en_clean.json      # TMDB data
│   ├── data_demo_spaceship.json          # Demo data
│   └── readyapi_instructions.json        # Docs
├── deploy/
│   ├── nginx.conf              # Reverse proxy config
│   └── docker-compose.yml      # Container orchestration
└── requirements.txt            # Python dependencies
```

### Code Statistics

- **Lines of Code**: ~3,500 (production code)
- **Test Coverage**: 4 comprehensive test suites
- **Documentation**: Extensive inline comments
- **Modularity**: Clear separation of concerns

---

## 📞 Author & Acknowledgments

**Author**: Esteban Bardolet  
**Thesis Title**: ReadyAPI: A Self-Hosted Semantic Search Platform  
**Date**: April 2026  
**Email**: info@readyapi.net

### Technology Attribution

- **Snowflake** for Arctic embeddings model
- **Chroma** for excellent vector database
- **FastAPI** community for fantastic framework
- **Hugging Face** for transformers library
- **scikit-learn** for BM25 implementation

---

**Thank you for reviewing this thesis project!**

For questions or clarifications, please contact: **info@readyapi.net**

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

**Live server**: readyapi.net

- **OS**: Linux
- **Web Server**: nginx (SSL/TLS)
- **App Server**: Gunicorn + Uvicorn (4 workers)
- **Database**: PostgreSQL
- **Storage**: 137MB for vector data
- **Uptime**: Monitored with health checks

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

## 📝 License

© 2026 Esteban Bardolet. All rights reserved.
This software is proprietary and confidential.

---

## 📞 Support & Questions

- 📖 **Documentation**: [https://readyapi.net/docs](https://readyapi.net/docs)
- 🎮 **Live Demos**: [https://readyapi.net/demos](https://readyapi.net/demos)
- 📧 **Email**: info@readyapi.net

---

## 🙏 Acknowledgments

- **Snowflake** for Arctic embeddings model
- **Chroma** for excellent vector database
- **FastAPI** community for fantastic framework
- **Hugging Face** for transformers library

---

**Made by Esteban**
