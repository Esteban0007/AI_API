#!/usr/bin/env python3
"""
Bulk Upload Test - 10,000 Documents in Batches
Splits into 1,000-doc batches to avoid memory exhaustion on server
"""

import requests
import time

API_URL = "https://api.readyapi.net/api/v1/documents/upload"
API_KEY = "rapi_5DAsNmjt5iDxYLPVKzqF__rDSzpoBLA90P5-THRrX98"
NUM_DOCS = 10000
BATCH_SIZE = 100  # Small batches to fit in 221MB free memory

print("\n" + "=" * 70)
print(f"BULK UPLOAD TEST - {NUM_DOCS:,} documents (batches of {BATCH_SIZE:,})")
print("=" * 70)
print(f"Note: Sending {NUM_DOCS // BATCH_SIZE} requests × {BATCH_SIZE:,} docs\n")

# Create 10K documents
print(f"Preparing {NUM_DOCS:,} documents...")
all_documents = []
for i in range(1, NUM_DOCS + 1):
    all_documents.append(
        {
            "id": f"doc-{i:06d}",
            "title": f"Machine Learning Basics #{i}",
            "content": "Machine learning is a subset of artificial intelligence that enables systems to learn from data. It powers recommendations, image recognition, natural language processing, and autonomous systems.",
            "keywords": ["ml", "ai", "learning"],
            "metadata": {
                "category": "tutorial",
                "language": "en",
                "source": "https://example.com",
            },
        }
    )

print("Uploading...")

print(f"✓ Prepared {len(all_documents):,} documents\n")

# Upload in batches
total_uploaded = 0
total_failed = 0
failed_batches = []
start_time = time.time()

num_batches = (NUM_DOCS + BATCH_SIZE - 1) // BATCH_SIZE

try:
    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, NUM_DOCS)
        batch = all_documents[start_idx:end_idx]

        print(
            f"Batch {batch_num + 1}/{num_batches}: Uploading {len(batch)} documents...",
            end=" ",
            flush=True,
        )

        try:
            batch_start = time.time()
            response = requests.post(
                API_URL,
                headers={"x-api-key": API_KEY},
                json={"documents": batch},
                timeout=120,  # 2 minutes per batch
            )
            batch_time = time.time() - batch_start

            if response.status_code == 200:
                data = response.json()
                uploaded = data.get("uploaded_count", 0)
                failed = data.get("failed_count", 0)
                total_uploaded += uploaded
                total_failed += failed
                print(f"✓ {uploaded:,} ok, {failed} fail ({batch_time:.1f}s)")
            else:
                print(f"✗ Status {response.status_code}")
                failed_batches.append(batch_num + 1)
                total_failed += len(batch)

        except Exception as e:
            print(f"✗ ERROR: {str(e)[:50]}")
            failed_batches.append(batch_num + 1)
            total_failed += len(batch)

except Exception as e:
    print(f"\n❌ CRITICAL ERROR: {type(e).__name__} - {str(e)[:100]}")

total_time = time.time() - start_time

print(f"\n" + "=" * 70)
print("FINAL RESULTS")
print("=" * 70)
print(f"Total time: {total_time:.2f}s")
print(f"Uploaded: {total_uploaded:,} / {NUM_DOCS:,}")
print(f"Failed: {total_failed:,}")
print(f"Throughput: {NUM_DOCS / total_time:.1f} docs/s")

if failed_batches:
    print(f"\n⚠️  Failed batches: {failed_batches}")
    print("❌ PARTIAL SUCCESS")
elif total_uploaded == NUM_DOCS:
    print("\n✅ SUCCESS - All documents uploaded!")
else:
    print(f"\n⚠️  INCOMPLETE - Only {total_uploaded:,} of {NUM_DOCS:,} uploaded")

print("=" * 70 + "\n")
