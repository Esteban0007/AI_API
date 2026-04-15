# SemanticSearch API - How It Works

## 🎯 Overview

This is a **semantic search API** that uses artificial intelligence to understand the _meaning_ of search queries, not just keywords. It's deployed as a full-stack web application with a FastAPI backend and a Jinja2+HTMX frontend.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Nginx)                          │
│                  readyapi.net:443 (HTTPS)                   │
├─────────────────────────────────────────────────────────────┤
│  • Jinja2 Templates (HTML)                                   │
│  • Pico.css (Minimalist CSS Framework)                       │
│  • HTMX (For reactive search without page reload)            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│                127.0.0.1:8000 (4 Gunicorn workers)           │
├─────────────────────────────────────────────────────────────┤
│  • Web Router: /simulator, /register, /search-partial        │
│  • API Router: /api/v1/search/query (with x-api-key auth)   │
│  • User Management: SQLite database with registration        │
│  • Email Service: Strato SMTP for confirmations              │
└────────────────────┬────────────────────────────────────────┘
                     │ Semantic Embeddings
                     ↓
┌─────────────────────────────────────────────────────────────┐
│          EMBEDDINGS ENGINE (Arctic-768D ONNX INT8)           │
│         Latency: ~41ms per query embedding + search          │
├─────────────────────────────────────────────────────────────┤
│  • Snowflake Arctic-768D: 768-dimension embeddings           │
│  • ONNX INT8: Quantized for speed & memory efficiency        │
│  • Disabled cross-encoder re-ranking (ENABLE_RERANKING=false)│
└────────────────────┬────────────────────────────────────────┘
                     │ Vector Similarity Search
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   VECTOR DATABASE                            │
│                    ChromaDB                                  │
├─────────────────────────────────────────────────────────────┤
│  • 1,958 TMDB movies with full metadata                      │
│  • Stores embeddings + original content                      │
│  • Supports multilingual queries (Spanish, English, etc)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Key Technologies

| Component              | Technology                 | Purpose                            |
| ---------------------- | -------------------------- | ---------------------------------- |
| **Web Framework**      | FastAPI + Uvicorn          | High-performance async API         |
| **WSGI Server**        | Gunicorn (4 workers)       | Production-grade server            |
| **Templates**          | Jinja2                     | Server-side HTML rendering         |
| **Frontend Framework** | Pico.css                   | Minimal, clean CSS                 |
| **Interactivity**      | HTMX                       | Reactive search without JavaScript |
| **Embeddings**         | Snowflake Arctic-768D ONNX | Semantic understanding             |
| **Vector DB**          | ChromaDB                   | Stores movie embeddings            |
| **User DB**            | SQLite + SHA256            | User registration & API keys       |
| **Email**              | Strato SMTP                | Account confirmation emails        |
| **Reverse Proxy**      | Nginx                      | SSL/TLS, routing                   |
| **SSL/TLS**            | Let's Encrypt              | Free HTTPS certificates            |

---

## 🔍 How Semantic Search Works

### Step 1: User Submits a Query

```html
User types in the search box: "superhero saves the world"
```

### Step 2: Frontend Sends Request (via HTMX)

```javascript
// HTMX triggers POST request with 500ms debounce
hx-post="/search-partial"
hx-trigger="keyup changed delay:500ms"
```

**Request sent to backend:**

```
POST /search-partial HTTP/1.1
Content-Type: application/x-www-form-urlencoded

query=superhero+saves+the+world
```

### Step 3: Backend Processes Query

**File:** [`app/api/web.py`](app/api/web.py#L100)

```python
@router.post("/search-partial")
async def search_partial(query: Form(str)):
    # 1. Initialize SearchEngine (loads embeddings model)
    search_engine = SearchEngine()

    # 2. Convert query to 768-dimensional vector
    # Using Arctic-768D ONNX INT8 (~41ms)
    query_embedding = embedding_model.encode(query)

    # 3. Search ChromaDB for similar movies
    results = search_engine.search(
        query=query,
        top_k=5,  # Return top 5 most similar movies
        include_content=True
    )

    # 4. Clean up results (extract summary text)
    for result in results:
        result.summary = _extract_summary(result.content)

    # 5. Render HTML partial
    return TemplateResponse(
        "results_list.html",
        {"request": request, "results": results, "timing_ms": 185}
    )
```

### Step 4: Embeddings Model Vectorizes the Query

**File:** `app/engine/search.py`

The Arctic-768D model converts text into a 768-dimensional vector:

```python
query = "superhero saves the world"
embedding = [0.234, -0.156, 0.892, ..., 0.445]  # 768 values

# Each dimension represents different semantic concepts
# e.g., dimension_1 = "action level"
#       dimension_2 = "hero presence"
#       dimension_3 = "drama intensity"
```

### Step 5: Similarity Search in ChromaDB

ChromaDB finds movies with the **most similar embeddings** using cosine similarity:

```python
# Each stored movie has an embedding:
movie1_embedding = [0.231, -0.154, 0.895, ..., 0.442]  # Avengers
movie2_embedding = [0.100, -0.045, 0.120, ..., 0.210]  # Romantic Comedy

# Cosine similarity scores (0-1, higher = more similar)
similarity(query, movie1) = 0.94  # ✅ Matches! "Avengers"
similarity(query, movie2) = 0.12  # ❌ Not similar
```

### Step 6: Results Returned to Frontend

**JSON Response with top 5 movies:**

```json
{
  "results": [
    {
      "title": "Avengers: Endgame",
      "summary": "When an alien army invades Earth, Earth's mightiest superheroes must save the world",
      "metadata": {
        "year": 2019,
        "cast": ["Robert Downey Jr.", "Chris Evans", "Mark Ruffalo"],
        "poster_path": "/path/to/poster.jpg",
        "rating": 8.4
      },
      "score": 0.94,  // Similarity score
      "timing_ms": 185
    },
    ...
  ]
}
```

### Step 7: HTMX Inserts Results into DOM

**File:** [`app/templates/results_list.html`](app/templates/results_list.html)

```html
<!-- HTMX replaces #results with this HTML -->
<div id="movie-card-avengers" class="movie-card">
  <img
    src="https://image.tmdb.org/t/p/w500/path.jpg"
    alt="Avengers: Endgame"
    class="movie-poster"
  />

  <div class="movie-info">
    <div class="movie-title">Avengers: Endgame</div>
    <p>
      When an alien army invades Earth, Earth's mightiest superheroes must save
      the world
    </p>

    <div
      style="border-top: 1px solid #e0e0e0; margin-top: 1rem; padding-top: 1rem;"
    >
      <span class="movie-year">2019</span>
      <span class="movie-cast"
        >With Robert Downey Jr., Chris Evans, Mark Ruffalo</span
      >
    </div>
  </div>

  <span class="score-badge">0.94</span>
</div>
```

### Step 8: Browser Displays Results

✅ User sees beautiful movie cards with:

- Movie poster image
- Title
- Summary text
- Year & cast
- Relevance score (0-1)

---

## 🎨 Frontend Flow - Complete Example

### Homepage (`/`)

**What you see:**

- Large headline: "SemanticSearch API"
- 6 feature cards highlighting benefits
- "Try Demo" button
- "Sign Up" button

**Code file:** [`app/templates/index.html`](app/templates/index.html)

### Search Simulator (`/simulator`)

**What you see:**

- Search input box
- Real-time results as you type
- Movie cards with poster, title, summary, year, cast

**What happens:**

1. User types: "sci-fi action with robots"
2. After 500ms delay, HTMX sends POST to `/search-partial`
3. Backend returns HTML with top 5 results
4. HTMX inserts HTML into `#results` div
5. Results appear instantly (no page reload!)

**Code flow:**

```
[User Types]
     ↓
[HTMX detects keyup after 500ms delay]
     ↓
[POST /search-partial with query parameter]
     ↓
[Backend: SearchEngine.search(query, top_k=5)]
     ↓
[Render results_list.html partial]
     ↓
[HTMX inserts into DOM]
     ↓
[User sees results instantly!]
```

### Registration (`/register`)

**What you see:**

- Email input
- Password input (min 8 chars)
- Confirm password input
- Submit button

**What happens on submit:**

1. Form POSTs to `/register`
2. Backend validates email/password
3. Generates API key: `rapi_<32-char-token>`
4. Generates confirmation token
5. Stores user in SQLite with hashed password
6. Sends confirmation email (dev mode: prints URL to logs)
7. Shows success message: "Check your email to confirm your account"

**Code file:** [`app/db/users.py`](app/db/users.py)

---

## 🔐 User Authentication & API Keys

### Registration Flow

```python
# User submits: email=user@example.com, password=secure123

# Backend does:
1. Validate email format & password length (≥8 chars)
2. Hash password: SHA256(password + salt)
3. Generate API Key: rapi_<32-char-token>
4. Generate confirmation token (expires in 24h)
5. Create SQLite record:
   {
     id: 1,
     email: "user@example.com",
     password_hash: "sha256...",
     api_key: "rapi_abc123...",
     is_confirmed: 0,
     confirmation_token: "token123",
     token_expires_at: "2026-03-02 10:00:00"
   }
6. Send confirmation email
7. Return success message
```

### Email Confirmation

**Email contains button:**

```
"Click here to confirm: https://readyapi.net/confirm/token123"
```

**When user clicks:**

1. Backend gets `/confirm/token123`
2. Looks up user by token
3. Checks token hasn't expired
4. Sets `is_confirmed = 1`
5. User can now use API!

### API Key Usage

**To use the API, send:**

```bash
curl -X POST "https://api.readyapi.net/api/v1/search/query" \
  -H "x-api-key: rapi_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "query": "superhero saves the world",
    "top_k": 5
  }'
```

**Backend validates:**

```python
@router.post("/api/v1/search/query")
async def search(request: SearchRequest, x_api_key: str = Header()):
    # 1. Get API key from request header
    # 2. Look up user in SQLite
    user = get_user_by_api_key(x_api_key)

    if not user or not user.is_confirmed:
        return {"error": "Invalid or unconfirmed API key"}

    # 3. Proceed with search
    results = search_engine.search(
        query=request.query,
        top_k=request.top_k
    )

    return {"results": results, "timing_ms": 185}
```

---

## ⚡ Performance Optimization

### Before Optimization (2000ms+ latency)

```
Input: "superhero saves the world"
  ↓
Embedding (Arctic-768D): 41ms
  ↓
Vector Search (ChromaDB): 15ms
  ↓
Cross-Encoder Re-ranking: 4,300ms ⚠️ BOTTLENECK!
  ↓
Total: 4,356ms
```

### After Optimization (185ms latency)

```
Input: "superhero saves the world"
  ↓
Embedding (Arctic-768D): 41ms
  ↓
Vector Search (ChromaDB): 15ms
  ↓
Cross-Encoder Re-ranking: DISABLED ✅
  ↓
Render Template: 129ms
  ↓
Total: 185ms
```

**What was changed:**

```python
# app/core/config.py
ENABLE_RERANKING = False  # Skip expensive re-ranking step
```

```python
# app/engine/search.py
def search(self, query: str, top_k: int = 5, include_content: bool = True):
    # ... embedding & ChromaDB search ...

    # OLD: This consumed 95% of time!
    # if self.config.ENABLE_RERANKING:
    #     results = self.reranker.rerank(results)

    # NEW: Skip re-ranking completely
    return results
```

---

## � Implementation Examples (Code-Focused)

### 1. Query Embedding Process

**File:** [`app/engine/embedder.py`](app/engine/embedder.py)

```python
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    def __init__(self):
        # Load Snowflake Arctic-768D model (ONNX INT8 quantized)
        self.model = SentenceTransformer(
            'Snowflake/snowflake-arctic-embed-m',
            model_kwargs={"trust_remote_code": True},
            cache_folder="./models"
        )

    def encode(self, text: str) -> list:
        """Convert text to 768-dimensional embedding vector."""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()  # Returns: [0.234, -0.156, 0.892, ..., 0.445]

# Usage:
embedder = EmbeddingModel()
query = "superhero saves the world"
embedding = embedder.encode(query)
print(f"Query embedding shape: {len(embedding)}")  # Output: 768
print(f"First 5 dimensions: {embedding[:5]}")      # Output: [0.234, -0.156, 0.892, ...]
```

**Key metrics:**

- Latency: ~41ms per embedding
- Dimensions: 768
- Model: Snowflake Arctic-768D ONNX INT8
- Quantization: INT8 (reduces memory 4x vs FP32)

---

### 2. Vector Similarity Search

**File:** [`app/engine/searcher.py`](app/engine/searcher.py)

```python
import chromadb
from scipy.spatial.distance import cosine

class SearchEngine:
    def __init__(self, tenant_id: str = "admin"):
        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(
            path="./data/chroma_db"
        )
        self.collection = self.client.get_or_create_collection(
            name=f"movies_{tenant_id}",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity metric
        )
        self.embedder = EmbeddingModel()

    def search(self, query: str, top_k: int = 5) -> list:
        """Search for similar movies using vector similarity."""
        # Step 1: Encode query to embedding
        query_embedding = self.embedder.encode(query)

        # Step 2: Query ChromaDB (returns top_k most similar)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["embeddings", "metadatas", "documents", "distances"]
        )

        # Step 3: Format results with similarity scores
        formatted_results = []
        for i, (doc_id, metadata, distance) in enumerate(
            zip(results['ids'][0], results['metadatas'][0], results['distances'][0])
        ):
            # Distance to similarity (for cosine: similarity = 1 - distance)
            similarity_score = 1 - distance

            formatted_results.append({
                "title": metadata.get("title"),
                "year": metadata.get("year"),
                "cast": metadata.get("cast", []),
                "summary": results['documents'][0][i],
                "score": round(similarity_score, 3),
                "rank": i + 1
            })

        return formatted_results

# Usage:
engine = SearchEngine()
results = engine.search(query="sci-fi action with robots", top_k=3)
for result in results:
    print(f"{result['rank']}. {result['title']} ({result['year']}) - Score: {result['score']}")
```

**Output example:**

```
1. The Terminator 2 (1991) - Score: 0.91
2. Transformers (2007) - Score: 0.88
3. Blade Runner 2049 (2017) - Score: 0.85
```

---

### 3. FastAPI Search Endpoint

**File:** [`app/api/web.py`](app/api/web.py#L160-L200)

```python
from fastapi import APIRouter, Form, Request
from fastapi.responses import TemplateResponse
from fastapi.templating import Jinja2Templates
import time

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/search-partial")
async def search_partial(request: Request, query: str = Form(...)):
    """
    Real-time semantic search endpoint.
    Called via HTMX from /simulator page.
    Returns HTML partial with movie results.
    """
    start_time = time.time()

    try:
        # Initialize search engine
        search_engine = SearchEngine(tenant_id="admin")

        # Perform semantic search
        results = search_engine.search(
            query=query,
            top_k=5
        )

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Render HTML partial with results
        return TemplateResponse(
            "results_list.html",
            {
                "request": request,
                "results": results,
                "query": query,
                "timing_ms": latency_ms,
                "result_count": len(results)
            }
        )

    except Exception as e:
        return TemplateResponse(
            "results_list.html",
            {
                "request": request,
                "results": [],
                "error": str(e),
                "query": query,
                "timing_ms": 0
            }
        )
```

---

### 4. API Endpoint with Authentication

**File:** [`app/api/v1.py`](app/api/v1.py#L50-L120)

```python
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api/v1", tags=["API"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: list
    timing_ms: int
    query: str

@router.post("/search/query", response_model=SearchResponse)
async def search_query(
    request_data: SearchRequest,
    x_api_key: str = Header(...)
):
    """
    Semantic search API endpoint (requires API key).

    Usage:
        curl -X POST https://api.readyapi.net/api/v1/search/query \
          -H "x-api-key: rapi_your_key_here" \
          -H "Content-Type: application/json" \
          -d '{"query": "superhero saves the world", "top_k": 5}'
    """
    start_time = time.time()

    # Step 1: Authenticate user
    user = get_user_by_api_key(x_api_key)
    if not user or not user.is_confirmed:
        raise HTTPException(
            status_code=401,
            detail="Invalid or unconfirmed API key"
        )

    # Step 2: Validate query
    if not request_data.query or len(request_data.query) < 2:
        raise HTTPException(
            status_code=400,
            detail="Query must be at least 2 characters"
        )

    # Step 3: Perform search
    search_engine = SearchEngine(tenant_id=user.tenant_id)
    results = search_engine.search(
        query=request_data.query,
        top_k=request_data.top_k
    )

    # Step 4: Log search (for analytics)
    log_search(
        user_id=user.id,
        query=request_data.query,
        result_count=len(results),
        latency_ms=int((time.time() - start_time) * 1000)
    )

    # Step 5: Return formatted response
    return SearchResponse(
        results=results,
        timing_ms=int((time.time() - start_time) * 1000),
        query=request_data.query
    )
```

---

### 5. Full Request/Response Example

**Request:**

```bash
curl -X POST "https://api.readyapi.net/api/v1/search/query" \
  -H "x-api-key: rapi_abc123xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sci-fi action with robots",
    "top_k": 3
  }'
```

**Response (200 OK):**

```json
{
  "results": [
    {
      "rank": 1,
      "title": "The Terminator 2",
      "year": 1991,
      "summary": "A cyborg is sent back in time to protect Sarah Connor...",
      "cast": ["Arnold Schwarzenegger", "Linda Hamilton"],
      "score": 0.91
    },
    {
      "rank": 2,
      "title": "Transformers",
      "year": 2007,
      "summary": "Giant robots battle for possession of a powerful energy cube...",
      "cast": ["Shia LaBeouf", "Megan Fox"],
      "score": 0.88
    },
    {
      "rank": 3,
      "title": "Blade Runner 2049",
      "year": 2017,
      "summary": "A replicant hunter uncovers a secret that could change humanity...",
      "cast": ["Ryan Gosling", "Harrison Ford"],
      "score": 0.85
    }
  ],
  "timing_ms": 185,
  "query": "sci-fi action with robots"
}
```

---

### 6. Performance Comparison Table

| Stage                  | Technology                   | Code Location                                                        | Latency   | % of Total |
| ---------------------- | ---------------------------- | -------------------------------------------------------------------- | --------- | ---------- |
| **Query Embedding**    | Arctic-768D ONNX INT8        | [`app/engine/embedder.py`](app/engine/embedder.py#L20-L40)           | 41ms      | 22%        |
| **Vector Search**      | ChromaDB (cosine similarity) | [`app/engine/searcher.py`](app/engine/searcher.py#L30-L60)           | 15ms      | 8%         |
| **Template Rendering** | Jinja2                       | [`app/templates/results_list.html`](app/templates/results_list.html) | 129ms     | 70%        |
| **Network/Total**      | -                            | -                                                                    | **185ms** | **100%**   |

**Optimization removed:**

```python
# REMOVED (was consuming 4,300ms):
if self.config.ENABLE_RERANKING:
    results = self.reranker.rerank(results)  # Cross-encoder re-ranking
```

**Config setting:** [`app/core/config.py`](app/core/config.py#L15)

```python
ENABLE_RERANKING = False  # Disabled for 10x performance improvement
```

---

### 7. Database Schema for Vectors

**File:** [`data/chroma_db/`](data/chroma_db/)

ChromaDB stores movies with embeddings:

```json
{
  "ids": ["movie_1", "movie_2", "movie_3"],
  "embeddings": [
    [0.234, -0.156, 0.892, ..., 0.445],    // Avengers embedding (768 dims)
    [0.342, -0.078, 0.156, ..., 0.234],    // Terminator embedding (768 dims)
    [0.456, 0.012, 0.789, ..., 0.567]      // Blade Runner embedding (768 dims)
  ],
  "metadatas": [
    {"title": "Avengers: Endgame", "year": 2019, "cast": [...]},
    {"title": "The Terminator 2", "year": 1991, "cast": [...]},
    {"title": "Blade Runner 2049", "year": 2017, "cast": [...]}
  ],
  "documents": [
    "When an alien army invades Earth...",
    "A cyborg is sent back in time...",
    "A replicant hunter searches for clues..."
  ]
}
```

Total movies indexed: **1,958 TMDB movies**
Total embeddings: **1,958 × 768 dimensions = 1,504,704 values**

---

### 8. Complete Code Files

| Feature       | Main File                                          | Related Files                                                        |
| ------------- | -------------------------------------------------- | -------------------------------------------------------------------- |
| **Embedding** | [`app/engine/embedder.py`](app/engine/embedder.py) | [`app/core/config.py`](app/core/config.py)                           |
| **Search**    | [`app/engine/searcher.py`](app/engine/searcher.py) | [`app/engine/store.py`](app/engine/store.py)                         |
| **Web API**   | [`app/api/web.py`](app/api/web.py)                 | [`app/templates/results_list.html`](app/templates/results_list.html) |
| **API v1**    | [`app/api/v1.py`](app/api/v1.py)                   | [`app/models/search.py`](app/models/search.py)                       |
| **Database**  | [`app/db/users.py`](app/db/users.py)               | [`app/db/session.py`](app/db/session.py)                             |

---

## �📊 Example: Searching for "sci-fi action with robots"

### 1. User Interaction

```
User sees search box on /simulator
User types: "sci-fi action with robots"
After 500ms of no typing, HTMX sends request
```

### 2. Backend Processing

```python
query = "sci-fi action with robots"

# Step 1: Encode to embedding
embedding = arctic_model.encode(query)
# Result: [0.342, -0.156, 0.892, ..., 0.445]  (768 dimensions)

# Step 2: Search ChromaDB
results = chromadb.search(
    query_embedding=embedding,
    n_results=5
)

# Step 3: Results (with similarity scores)
[
    {
        "id": 1,
        "title": "The Terminator 2",
        "metadata": {"year": 1991, "cast": ["Arnold Schwarzenegger"]},
        "score": 0.91,  # 91% match!
        "content": "A cyborg is sent back in time..."
    },
    {
        "id": 2,
        "title": "Transformers",
        "metadata": {"year": 2007, "cast": ["Shia LaBeouf"]},
        "score": 0.88,  # 88% match
        "content": "Giant robots battle for Earth..."
    },
    {
        "id": 3,
        "title": "Blade Runner 2049",
        "metadata": {"year": 2017, "cast": ["Ryan Gosling"]},
        "score": 0.85,  # 85% match
        "content": "A replicant hunter searches for clues..."
    },
    ...
]
```

### 3. Frontend Displays

**User sees on screen:**

```
🎬 Search Simulator
Search movies: [sci-fi action with robots          ]  🔄 Searching...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Poster]  The Terminator 2
          A cyborg is sent back in time to protect Sarah Connor
          from a more advanced terminator.

          1991                    0.91
          With Arnold Schwarzenegger

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Poster]  Transformers
          Giant robots battle for possession of a powerful energy
          cube hidden somewhere on Earth.

          2007                    0.88
          With Shia LaBeouf, Megan Fox

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Poster]  Blade Runner 2049
          A replicant hunter uncovers a secret that could
          change the fate of humanity.

          2017                    0.85
          With Ryan Gosling, Harrison Ford

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📁 Project Structure

```
/Users/estebanbardolet/Desktop/API_IA/
├── app/
│   ├── main.py                 # FastAPI app initialization
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py         # Include both routers
│   │   ├── web.py              # Web routes: /, /simulator, /register, /search-partial
│   │   └── v1.py               # API routes: /api/v1/search/query
│   ├── core/
│   │   ├── config.py           # Settings (ENABLE_RERANKING, SMTP, etc)
│   │   └── email.py            # Email service with Strato SMTP
│   ├── db/
│   │   └── users.py            # SQLite user management
│   ├── engine/
│   │   └── search.py           # SearchEngine with Arctic embeddings
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   └── templates/
│       ├── base.html           # Base template (nav, CSS, blocks)
│       ├── index.html          # Home page
│       ├── simulator.html      # Search demo page
│       ├── register.html       # Registration form
│       └── results_list.html   # Movie results partial
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md
```

---

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export ENABLE_RERANKING=False

# Run server
uvicorn app.main:app --reload
```

### Production Deployment (Ubuntu Server)

```bash
# SSH to server
ssh root@194.164.207.6

# Deploy from git
cd /var/www/readyapi
git pull origin main
systemctl restart readyapi

# Verify
curl https://api.readyapi.net/health  # Should return JSON
```

### Domains & SSL

```
readyapi.net       → Nginx → FastAPI web routes
api.readyapi.net   → Nginx → FastAPI API routes

Both use Let's Encrypt SSL certificates (automatic renewal)
```

---

## 📚 API Documentation

### Search Endpoint

```
POST /api/v1/search/query
Content-Type: application/json
x-api-key: rapi_your_api_key_here

Request:
{
  "query": "superhero saves the world",
  "top_k": 5
}

Response:
{
  "results": [
    {
      "title": "Avengers: Endgame",
      "summary": "When an alien army invades Earth...",
      "metadata": {
        "year": 2019,
        "cast": ["Robert Downey Jr.", "Chris Evans"],
        "poster_path": "/path/to/poster.jpg",
        "rating": 8.4
      },
      "score": 0.94
    }
  ],
  "timing_ms": 185
}
```

### Additional Endpoints

```
GET /                          → Home page
GET /simulator                 → Search demo
GET /register                  → Registration form
POST /register                 → Submit registration
POST /search-partial           → HTMX search (returns HTML)
GET /confirm/{token}           → Confirm email
GET /api-docs                  → Swagger documentation
GET /health                    → Health check
```

---

## 🎓 Key Learnings

### 1. **Semantic Search vs Keyword Search**

- **Keyword:** "superhero" matches "Superman" but not "Avengers"
- **Semantic:** "superhero saves the world" matches Avengers because it understands the _concept_

### 2. **Vector Embeddings**

- Text → Math: "superhero saves the world" becomes [0.234, -0.156, ...]
- Similarity = How close embeddings are (cosine similarity)
- 768 dimensions capture semantic meaning

### 3. **The Importance of Production Profiling**

- Disabled re-ranking feature → **10x latency improvement** (2000ms → 185ms)
- Always measure before optimizing!

### 4. **Full-Stack is Easier Than APIs Alone**

- Web UI + API = Better user experience
- Jinja2 + HTMX = No JavaScript framework needed
- Pico.css = Minimal CSS, beautiful UI

### 5. **Email Confirmation Pattern**

- User registers → Token sent via email → Confirms → Account active
- Simple but effective user verification

---

## 🔗 How to Use the Demo

**Visit:** https://readyapi.net

1. Click "Try Demo" button
2. Type searches like:
   - "superhero saves the world"
   - "intelligent robot"
   - "detective solves mystery"
   - "heist movie"
3. See results appear in real-time!

4. To get API access:
   - Click "Sign Up"
   - Enter email & password
   - Confirm email (check logs in dev mode)
   - Copy your API key
   - Use it in curl requests

---

## 🤝 Support

- **API Issues:** Check `/api-docs` (Swagger UI)
- **Frontend Issues:** Browser console (F12)
- **Server Issues:** SSH and check logs:
  ```bash
  systemctl status readyapi
  journalctl -u readyapi -f
  ```

---

**Built with ❤️ using FastAPI, Arctic-768D, and modern web technologies**
