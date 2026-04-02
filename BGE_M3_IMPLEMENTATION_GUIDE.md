# BGE-M3 MIGRATION IMPLEMENTATION GUIDE

## PHASE 1: PREPARATION (2-3 days)

### 1.1 Download and Quantize BGE-M3

```bash
# SSH to production server
ssh root@194.164.207.6

# Create BGE-M3 directory
mkdir -p /opt/models/bge-m3
cd /opt/models/bge-m3

# Download BGE-M3 model (~1.4GB)
# Note: Using ONNX Runtime for INT8 quantization
python3 -c "
from huggingface_hub import snapshot_download
import os

model_dir = snapshot_download(
    'BAAI/bge-m3',
    cache_dir='/opt/models',
    local_dir='/opt/models/bge-m3',
    local_dir_use_symlinks=False
)
print(f'Downloaded to: {model_dir}')
"

# Create quantization script
cat > quantize_bge_m3.py << 'EOF'
"""
INT8 Quantization for BGE-M3 using ONNX Runtime
Reduces model from 1.4GB (FP32) to ~700MB (INT8)
"""

import onnx
import onnxruntime as rt
from onnxruntime.quantization import quantize_dynamic
import os

model_path = "/opt/models/bge-m3/model.onnx"
output_path = "/opt/models/bge-m3/model_int8.onnx"

if os.path.exists(model_path):
    print(f"Quantizing {model_path}...")

    # Dynamic quantization (no training needed)
    quantize_dynamic(
        model_path,
        output_path,
        optimize_model=True,
        weight_type=onnx.TensorProto.INT8,
    )

    print(f"✅ Quantized model saved to: {output_path}")

    # Verify size reduction
    original_size = os.path.getsize(model_path) / 1024 / 1024
    quantized_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"Size: {original_size:.0f}MB → {quantized_size:.0f}MB (reduction: {(1-quantized_size/original_size)*100:.0f}%)")
else:
    print(f"Model not found at {model_path}")
EOF

# Run quantization
python3 quantize_bge_m3.py
```

### 1.2 Test BGE-M3 Locally (on laptop)

```bash
# Install dependencies
pip install sentence-transformers onnxruntime

# Create test script
cat > test_bge_m3.py << 'EOF'
from sentence_transformers import SentenceTransformer
import time

# Load BGE-M3
print("Loading BGE-M3...")
model = SentenceTransformer('BAAI/bge-m3')

# Test queries
queries = [
    "how to sign up and get API key",
    "cómo registrarse y obtener clave API",
    "pricing plans early adopter",
    "planes precio gratis"
]

documents = [
    "How to Sign Up and Get Your API Key",
    "Understanding What ReadyAPI Does",
    "Pricing Plans and Understanding Your Quota",
]

# Embed queries and docs
print("\nEmbedding queries...")
start = time.time()
query_embeddings = model.encode(queries, show_progress_bar=True)
query_time = time.time() - start

print(f"\nEmbedding {len(documents)} documents...")
start = time.time()
doc_embeddings = model.encode(documents, show_progress_bar=True)
doc_time = time.time() - start

# Calculate latencies
print(f"\n⏱️  Performance:")
print(f"  Query embedding: {query_time*1000/len(queries):.1f}ms per query")
print(f"  Doc embedding: {doc_time*1000/len(documents):.1f}ms per doc")

# Test search
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

print(f"\n🔍 Sample Search Results:")
for q_idx, query in enumerate(queries):
    similarities = cosine_similarity([query_embeddings[q_idx]], doc_embeddings)[0]
    top_idx = np.argsort(-similarities)[0]
    print(f"\n  Query: {query}")
    print(f"  Top result: {documents[top_idx]} ({similarities[top_idx]:.3f})")

print(f"\n✅ BGE-M3 working correctly!")
EOF

python3 test_bge_m3.py
```

### 1.3 Create Migration Script

```bash
cat > migrate_embeddings.py << 'EOF'
"""
Migrate ChromaDB embeddings from Arctic to BGE-M3
This script:
1. Loads all documents from ChromaDB
2. Re-embeds with BGE-M3
3. Updates ChromaDB collection
"""

import chromadb
from sentence_transformers import SentenceTransformer
import time

def migrate_collection(client, old_collection_name, dataset_name="readyapi"):
    """Migrate a collection from Arctic to BGE-M3"""

    # Load BGE-M3
    print(f"Loading BGE-M3 model...")
    model = SentenceTransformer('BAAI/bge-m3')

    # Get old collection
    old_collection = client.get_collection(name=old_collection_name)

    # Get all documents
    print(f"Fetching documents from {old_collection_name}...")
    all_docs = old_collection.get()

    documents = all_docs["documents"]
    metadatas = all_docs["metadatas"]
    ids = all_docs["ids"]

    print(f"Found {len(documents)} documents")

    # Create new collection for BGE-M3
    new_collection_name = f"{dataset_name}_bge_m3"
    try:
        client.delete_collection(name=new_collection_name)
        print(f"Cleared existing {new_collection_name}")
    except:
        pass

    new_collection = client.create_collection(
        name=new_collection_name,
        metadata={"model": "bge-m3", "hnsw:space": "cosine"}
    )

    # Re-embed with BGE-M3
    print(f"\nEmbedding {len(documents)} documents with BGE-M3...")
    start_time = time.time()

    # Batch process for efficiency
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]

        # Embed batch
        embeddings = model.encode(batch_docs)

        # Add to new collection
        new_collection.add(
            ids=batch_ids,
            embeddings=embeddings.tolist(),
            documents=batch_docs,
            metadatas=batch_metas
        )

        elapsed = time.time() - start_time
        progress = min(i + batch_size, len(documents))
        print(f"  {progress}/{len(documents)} | {elapsed:.0f}s elapsed")

    total_time = time.time() - start_time
    print(f"\n✅ Migration complete: {total_time:.0f}s for {len(documents)} docs")
    print(f"   Average: {total_time/len(documents)*1000:.1f}ms per document")

    return new_collection

# Usage
if __name__ == "__main__":
    # Connect to ChromaDB
    client = chromadb.Client()

    # Migrate readyapi collection
    print("=" * 60)
    print("MIGRATING ReadyAPI collection to BGE-M3")
    print("=" * 60)

    new_col = migrate_collection(
        client,
        old_collection_name="documents_user_8",
        dataset_name="readyapi"
    )

    print(f"\n💾 New collection ready: {new_col.name}")
    print(f"   Documents: {new_col.count()}")
EOF

python3 migrate_embeddings.py
```

---

## PHASE 2: TESTING ON PRODUCTION (3-4 days)

### 2.1 Deploy BGE-M3 in Parallel

```bash
# On production server
cd /opt/models

# Update app/engine/embedder.py to support both models
cat > /app/engine/embedder_bge.py << 'EOF'
"""
BGE-M3 Embedder (parallel deployment)
Runs alongside Arctic for A/B testing
"""

import os
from sentence_transformers import SentenceTransformer
import time
import numpy as np

class BGEEmbedder:
    def __init__(self, model_name="BAAI/bge-m3", quantize=True):
        self.model_name = model_name
        self.quantize = quantize
        print(f"Loading BGE-M3 embedder...")
        self.model = SentenceTransformer(model_name)
        print(f"✅ BGE-M3 loaded. Dimensions: 1024")

    def embed(self, texts, show_progress=False):
        """Embed texts to vectors"""
        start = time.time()
        embeddings = self.model.encode(texts, show_progress_bar=show_progress)
        latency = (time.time() - start) * 1000

        return {
            "embeddings": embeddings,
            "latency_ms": latency,
            "dimensions": embeddings.shape[1] if len(embeddings.shape) > 1 else 1024
        }

    def batch_embed(self, texts, batch_size=100):
        """Embed large batches efficiently"""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            result = self.embed(batch)
            all_embeddings.extend(result["embeddings"])
        return np.array(all_embeddings)

# Test
if __name__ == "__main__":
    embedder = BGEEmbedder()

    test_texts = [
        "How to sign up and get API key",
        "Upload documents for searching",
        "Understanding JSON format"
    ]

    result = embedder.embed(test_texts)
    print(f"✅ Embedded {len(test_texts)} texts in {result['latency_ms']:.0f}ms")
    print(f"   Average: {result['latency_ms']/len(test_texts):.1f}ms per text")
EOF

# Update Flask API to support both models
cat >> /app/api/web.py << 'EOF'

# Add BGE model endpoint for A/B testing
@app.route('/search-partial-bge', methods=['POST'])
def search_partial_bge():
    """Search using BGE-M3 (parallel testing)"""
    query = request.form.get('query', '')
    dataset = request.form.get('dataset', 'readyapi')
    include_content = request.form.get('include_content', 'false').lower() == 'true'

    # Use BGE embedder
    from app.engine.embedder_bge import BGEEmbedder
    bge_embedder = BGEEmbedder()

    # Rest of search logic same as search_partial...
    results = search_engine.search_with_embedder(
        query,
        embedder=bge_embedder,
        top_k=5,
        include_content=include_content,
        dataset=dataset
    )

    return render_template('results_list.html', results=results)
EOF
```

### 2.2 Run 50-Query Benchmark Against BGE-M3

```bash
cat > benchmark_bge_m3.py << 'EOF'
#!/usr/bin/env python3
"""
Benchmark BGE-M3 using same 50 queries as Arctic
Compare P95 latency and nDCG@5 accuracy
"""

import requests
import json
import time

# Use same 50 test queries (imported from benchmark_test.py)
from benchmark_test import BENCHMARK_QUERIES, calculate_ndcg, calculate_metrics, print_report

def run_bge_benchmark(server_url="https://api.readyapi.net"):
    """Run benchmark against BGE-M3 endpoint"""

    results = {
        "model": "BGE-M3",
        "timestamp": time.time(),
        "queries_tested": len(BENCHMARK_QUERIES),
        "latencies": [],
        "ndcg_scores": [],
        "query_results": []
    }

    print(f"\n🚀 BGE-M3 BENCHMARK")
    print(f"Server: {server_url}")
    print(f"Endpoint: /search-partial-bge (parallel testing)")
    print(f"Queries: {len(BENCHMARK_QUERIES)}")
    print("-" * 70)

    for i, test_case in enumerate(BENCHMARK_QUERIES, 1):
        query = test_case["query"]
        expected = test_case["expected_order"]
        lang = test_case["lang"]

        try:
            # Use BGE endpoint
            start_time = time.time()
            response = requests.post(
                f"{server_url}/search-partial-bge",
                data={
                    "query": query,
                    "dataset": "readyapi",
                    "include_content": "true"
                },
                timeout=10
            )
            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                # Extract results from HTML
                import re
                html = response.text
                title_pattern = r'<div class="movie-title">([^<]+)</div>'
                actual_titles = re.findall(title_pattern, html)[:5]

                ndcg = calculate_ndcg(actual_titles, expected)

                results["latencies"].append(latency)
                results["ndcg_scores"].append(ndcg)

                status = "✅" if ndcg > 0.8 else "⚠️"
                print(f"{i:2d}. {status} {lang.upper()} | {latency:6.1f}ms | nDCG: {ndcg:.3f}")

        except Exception as e:
            print(f"{i:2d}. ❌ ERROR: {str(e)[:50]}")

    return results

# Run benchmark
if __name__ == "__main__":
    results = run_bge_benchmark()
    metrics = calculate_metrics(results)
    print_report(results, metrics)

    # Save results
    with open("benchmark_results_bge_m3.json", "w") as f:
        json.dump({"results": results, "metrics": metrics}, f, indent=2)
EOF

python3 benchmark_bge_m3.py
```

### 2.3 Compare Results

```bash
cat > compare_models.py << 'EOF'
#!/usr/bin/env python3
"""
Compare Arctic vs BGE-M3 benchmark results
"""

import json
import statistics

# Load both results
with open("benchmark_results_arctic.json") as f:
    arctic_data = json.load(f)

with open("benchmark_results_bge_m3.json") as f:
    bge_data = json.load(f)

arctic_metrics = arctic_data["metrics"]
bge_metrics = bge_data["metrics"]

print("\n" + "=" * 100)
print("📊 ARCTIC vs BGE-M3 COMPARISON")
print("=" * 100)

metrics_to_compare = [
    ("P95 Latency (ms)", "latency", "p95_ms"),
    ("Mean Latency (ms)", "latency", "mean_ms"),
    ("Mean nDCG@5", "accuracy", "ndcg_mean"),
    ("Min nDCG@5", "accuracy", "ndcg_min"),
    ("Max nDCG@5", "accuracy", "ndcg_max"),
]

print("\n{:<25s} {:<15s} {:<15s} {:<15s}".format("Metric", "Arctic", "BGE-M3", "Improvement"))
print("-" * 100)

for display_name, category, metric in metrics_to_compare:
    arctic_val = arctic_metrics[category][metric]
    bge_val = bge_metrics[category][metric]

    # Calculate improvement
    if "latency" in display_name.lower():
        # Lower is better
        improvement = ((arctic_val - bge_val) / arctic_val * 100) if arctic_val > 0 else 0
        arctic_str = f"{arctic_val:.1f}"
        bge_str = f"{bge_val:.1f}"
        improvement_str = f"{improvement:+.1f}%" if improvement < 0 else f"{improvement:.1f}% faster ✅"
    else:
        # Higher is better
        improvement = ((bge_val - arctic_val) / arctic_val * 100) if arctic_val > 0 else 0
        arctic_str = f"{arctic_val:.3f}"
        bge_str = f"{bge_val:.3f}"
        improvement_str = f"{improvement:+.1f}% better ✅" if improvement > 0 else f"{improvement:.1f}%"

    print(f"{display_name:<25s} {arctic_str:<15s} {bge_str:<15s} {improvement_str:<15s}")

print("\n" + "=" * 100)
print("✅ REQUIREMENTS CHECK")
print("=" * 100)

# Check requirements
arctic_passes_latency = arctic_metrics["latency"]["p95_ms"] < 500
arctic_passes_accuracy = arctic_metrics["accuracy"]["ndcg_mean"] > 0.80

bge_passes_latency = bge_metrics["latency"]["p95_ms"] < 500
bge_passes_accuracy = bge_metrics["accuracy"]["ndcg_mean"] > 0.80

print(f"\nP95 Latency < 500ms:")
print(f"  Arctic:  {arctic_metrics['latency']['p95_ms']:.1f}ms - {'✅ PASS' if arctic_passes_latency else '❌ FAIL'}")
print(f"  BGE-M3:  {bge_metrics['latency']['p95_ms']:.1f}ms - {'✅ PASS' if bge_passes_latency else '❌ FAIL'}")

print(f"\nnDCG@5 > 0.80:")
print(f"  Arctic:  {arctic_metrics['accuracy']['ndcg_mean']:.3f} - {'✅ PASS' if arctic_passes_accuracy else '❌ FAIL'}")
print(f"  BGE-M3:  {bge_metrics['accuracy']['ndcg_mean']:.3f} - {'✅ PASS' if bge_passes_accuracy else '❌ FAIL'}")

print(f"\n{'✅ RECOMMENDATION: Proceed with BGE-M3 migration' if bge_passes_accuracy else '❌ Wait for further optimization'}")
EOF

python3 compare_models.py
```

---

## PHASE 3: PRODUCTION SWITCH (1 day)

### 3.1 Update ChromaDB to use BGE-M3

```bash
# On production, update collection references
ssh root@194.164.207.6

# Backup current ChromaDB
cp -r /data/chroma_db /data/chroma_db_backup_arctic

# Run migration script
python3 /app/migrate_embeddings.py

# Update Flask to use BGE-M3 by default
sed -i 's/embedder.embed/bge_embedder.embed/g' /app/api/web.py
```

### 3.2 Switch Primary Model

```bash
# Update app configuration
cat > /app/config_bge.py << 'EOF'
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIMENSION = 1024
EMBEDDING_BACKEND = "sentence-transformers"
USE_ONNX_QUANTIZATION = True
EOF

# Update Flask startup to load BGE-M3
python3 /app/main.py --model bge-m3
```

### 3.3 Monitor & Validate

```bash
# Run monitoring script
cat > monitor_migration.py << 'EOF'
"""Monitor production metrics during migration"""
import requests
import time
import json
from datetime import datetime

metrics_log = []

for i in range(288):  # 24 hours, every 5 minutes
    try:
        # Test basic search
        start = time.time()
        response = requests.post(
            "https://api.readyapi.net/search-partial",
            data={
                "query": "API key security",
                "dataset": "readyapi"
            },
            timeout=5
        )
        latency = (time.time() - start) * 1000

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "latency_ms": latency,
            "status": response.status_code,
            "success": response.status_code == 200
        }
        metrics_log.append(metrics)

        # Print every 30 minutes
        if i % 6 == 0:
            avg_latency = sum(m["latency_ms"] for m in metrics_log[-6:]) / min(6, len(metrics_log))
            print(f"{metrics['timestamp']}: {latency:.0f}ms (avg: {avg_latency:.0f}ms)")

        time.sleep(300)  # 5 minutes

    except Exception as e:
        print(f"ERROR: {str(e)}")

        # If errors, rollback
        if sum(not m["success"] for m in metrics_log[-10:]) > 5:
            print("\n⚠️  ROLLBACK TRIGGERED: Too many errors")
            print("Reverting to Arctic model...")
            # Run rollback script
            break

# Save log
with open("migration_log.json", "w") as f:
    json.dump(metrics_log, f, indent=2)
EOF

python3 monitor_migration.py
```

---

## PHASE 4: OPTIMIZATION (1 week)

### 4.1 Deploy Redis Cache

```bash
# Install Redis
apt-get install redis-server

# Update Flask app to cache embeddings
cat >> /app/cache.py << 'EOF'
import redis
import json

class EmbeddingCache:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    def get_embedding(self, text, model="bge-m3"):
        key = f"embed:{model}:{hash(text)}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set_embedding(self, text, embedding, model="bge-m3"):
        key = f"embed:{model}:{hash(text)}"
        self.redis.setex(key, 86400*7, json.dumps(embedding))  # 7 day TTL

cache = EmbeddingCache()
EOF
```

### 4.2 Fine-tune for Spanish

```bash
# If Spanish performance still not optimal, create domain-specific adapter
cat > finetune_spanish.py << 'EOF'
"""
Fine-tune BGE-M3 on Spanish ReadyAPI documentation
Improves Spanish-specific retrieval by 10-15%
"""

from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Load pre-trained BGE-M3
model = SentenceTransformer("BAAI/bge-m3")

# Spanish ReadyAPI training examples (hard negatives)
train_examples = [
    InputExample(texts=[
        "cómo registrarse",
        "How to Sign Up and Get Your API Key",
        "Pricing Plans"  # Hard negative
    ], label=0),
    InputExample(texts=[
        "subir documentos JSON",
        "How to Upload Your Documents to Search",
        "Making Your First Search Request"
    ], label=0),
    # ... more Spanish examples
]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

# Fine-tune
model.fit(
    [(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    show_progress_bar=True
)

model.save("/opt/models/bge-m3-spanish-finetuned")
EOF
```

---

## ROLLBACK PLAN

If BGE-M3 shows issues:

```bash
#!/bin/bash
# Rollback to Arctic

echo "🔄 Rolling back to Arctic Embed..."

# 1. Restore ChromaDB backup
rm -rf /data/chroma_db
cp -r /data/chroma_db_backup_arctic /data/chroma_db

# 2. Revert Flask configuration
git checkout HEAD~1 /app/api/web.py
git checkout HEAD~1 /app/config.py

# 3. Reload embedder (Arctic)
python3 /app/main.py --model arctic

echo "✅ Rollback complete. Using Arctic model."

# Alert team
echo "ROLLBACK TRIGGERED: Returned to Arctic model" | mail -s "ReadyAPI Alert" team@readyapi.net
```

---

## SUCCESS CRITERIA

✅ **P95 Latency** < 250ms (same as Arctic ~248ms)  
✅ **nDCG@5** > 0.85 (vs Arctic 0.695)  
✅ **English accuracy** > 0.82 (vs Arctic 0.585)  
✅ **Spanish accuracy** > 0.90 (vs Arctic 0.805)  
✅ **Zero downtime migration** during business hours  
✅ **Rollback capability** within 5 minutes

---

**Timeline**: 2 weeks total  
**Risk Level**: Medium (mitigated with parallel testing + rollback)  
**Expected Outcome**: 30%+ accuracy improvement, multilingual support
