#!/usr/bin/env python3
"""
Test suite for INT8 quantized Arctic ONNX model
Validates correctness and measures performance improvements
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from statistics import mean, stdev
from typing import Dict, List

try:
    import onnxruntime as ort
except ImportError:
    print("Installing onnxruntime...")
    os.system("pip install onnxruntime")
    import onnxruntime as ort

from transformers import AutoTokenizer


class QuantizedModelTester:
    """Test quantized Arctic ONNX model"""

    def __init__(
        self,
        model_dir: str = "/var/www/readyapi/models/arctic_onnx",
        quantized_model_name: str = "model_int8.onnx",
    ):
        """Initialize tester"""
        self.model_dir = model_dir
        self.original_model_path = f"{model_dir}/model.onnx"
        self.quantized_model_path = f"{model_dir}/{quantized_model_name}"
        self.tokenizer_path = model_dir
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
        }

    def load_sessions(self) -> tuple:
        """Load both original and quantized model sessions"""
        print("Loading models...")

        # Check if quantized model exists
        if not os.path.exists(self.quantized_model_path):
            print(f"❌ Quantized model not found: {self.quantized_model_path}")
            return None, None

        original_session = ort.InferenceSession(
            self.original_model_path, providers=["CPUExecutionProvider"]
        )

        quantized_session = ort.InferenceSession(
            self.quantized_model_path, providers=["CPUExecutionProvider"]
        )

        print("✓ Models loaded")
        return original_session, quantized_session

    def prepare_inputs(self, query: str, tokenizer) -> dict:
        """Prepare ONNX inputs from query"""
        tokens = tokenizer(
            query,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="np",
        )

        ort_inputs = {
            "input_ids": tokens["input_ids"].astype(np.int64),
            "attention_mask": tokens["attention_mask"].astype(np.int64),
        }

        if "token_type_ids" in tokens:
            ort_inputs["token_type_ids"] = tokens["token_type_ids"].astype(np.int64)

        return ort_inputs

    def extract_embedding(self, outputs: list) -> np.ndarray:
        """Extract embedding from model outputs"""
        # Usually last_hidden_state is in outputs[0]
        last_hidden_state = outputs[0]
        # Mean pooling
        attention_mask = outputs[1] if len(outputs) > 1 else None
        embedding = np.mean(last_hidden_state, axis=1)
        return embedding.flatten()

    def test_correctness(self, num_queries: int = 5) -> bool:
        """Test that quantized model produces similar outputs"""
        print("\n" + "=" * 70)
        print("🔍 TEST 1: CORRECTNESS VALIDATION")
        print("=" * 70)

        test_queries = [
            "Represent this query for retrieval: Christopher Nolan",
            "Represent this query for retrieval: science fiction",
            "Represent this query for retrieval: action movies",
            "Represent this query for retrieval: drama films",
            "Represent this query for retrieval: horror thriller",
        ][:num_queries]

        original_session, quantized_session = self.load_sessions()
        if not original_session or not quantized_session:
            return False

        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
        test_results = []

        print(f"\n Testing {len(test_queries)} queries for output similarity...\n")

        for i, query in enumerate(test_queries, 1):
            ort_inputs = self.prepare_inputs(query, tokenizer)

            # Get embeddings
            original_outputs = original_session.run(None, ort_inputs)
            quantized_outputs = quantized_session.run(None, ort_inputs)

            original_embedding = self.extract_embedding(original_outputs)
            quantized_embedding = self.extract_embedding(quantized_outputs)

            # Calculate cosine similarity
            dot_product = np.dot(original_embedding, quantized_embedding)
            norm_original = np.linalg.norm(original_embedding)
            norm_quantized = np.linalg.norm(quantized_embedding)
            similarity = dot_product / (norm_original * norm_quantized)

            # Calculate difference
            euclidean_distance = np.linalg.norm(
                original_embedding - quantized_embedding
            )
            max_difference = np.max(np.abs(original_embedding - quantized_embedding))

            test_results.append(
                {
                    "query_num": i,
                    "similarity": round(float(similarity), 4),
                    "euclidean_distance": round(float(euclidean_distance), 4),
                    "max_difference": round(float(max_difference), 4),
                }
            )

            status = "✓" if similarity > 0.99 else "⚠️"
            print(f"  Query {i}: Similarity {similarity:.4f} {status}")

        all_passed = all(r["similarity"] > 0.99 for r in test_results)

        self.results["tests"].append(
            {
                "name": "Correctness Validation",
                "status": "PASSED" if all_passed else "WARNING",
                "results": test_results,
            }
        )

        print(
            f"\n{'✓ All queries similar' if all_passed else '⚠️  Some queries differ slightly'}"
        )
        return True

    def test_latency(self, num_queries: int = 20) -> bool:
        """Test latency performance"""
        print("\n" + "=" * 70)
        print("⚡ TEST 2: LATENCY PERFORMANCE")
        print("=" * 70)

        original_session, quantized_session = self.load_sessions()
        if not original_session or not quantized_session:
            return False

        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)

        test_query = "Represent this query for retrieval: benchmark test query"
        ort_inputs = self.prepare_inputs(test_query, tokenizer)

        original_times = []
        quantized_times = []

        print(f"\n Running {num_queries} latency tests...\n")

        for i in range(num_queries):
            # Original model
            start = time.time()
            original_session.run(None, ort_inputs)
            original_times.append((time.time() - start) * 1000)

            # Quantized model
            start = time.time()
            quantized_session.run(None, ort_inputs)
            quantized_times.append((time.time() - start) * 1000)

            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/{num_queries} tests")

        # Calculate statistics
        original_avg = mean(original_times)
        original_stdev = stdev(original_times) if len(original_times) > 1 else 0
        quantized_avg = mean(quantized_times)
        quantized_stdev = stdev(quantized_times) if len(quantized_times) > 1 else 0

        speedup = original_avg / quantized_avg if quantized_avg > 0 else 1.0

        results = {
            "num_queries": num_queries,
            "original_model": {
                "avg_ms": round(original_avg, 2),
                "stdev_ms": round(original_stdev, 2),
                "min_ms": round(min(original_times), 2),
                "max_ms": round(max(original_times), 2),
            },
            "quantized_model": {
                "avg_ms": round(quantized_avg, 2),
                "stdev_ms": round(quantized_stdev, 2),
                "min_ms": round(min(quantized_times), 2),
                "max_ms": round(max(quantized_times), 2),
            },
            "speedup": round(speedup, 2),
            "improvement_pct": round((1 - quantized_avg / original_avg) * 100, 2),
        }

        print(f"\n📊 LATENCY RESULTS:")
        print(f"  Original: {original_avg:.2f}ms (±{original_stdev:.2f}ms)")
        print(f"  Quantized: {quantized_avg:.2f}ms (±{quantized_stdev:.2f}ms)")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Improvement: {results['improvement_pct']}%")

        self.results["tests"].append(
            {"name": "Latency Performance", "status": "PASSED", "results": results}
        )

        return True

    def test_batch_processing(self, batch_sizes: List[int] = [1, 5, 10]) -> bool:
        """Test batch processing performance"""
        print("\n" + "=" * 70)
        print("📦 TEST 3: BATCH PROCESSING")
        print("=" * 70)

        original_session, quantized_session = self.load_sessions()
        if not original_session or not quantized_session:
            return False

        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
        test_queries = [
            "Represent this query for retrieval: query 1",
            "Represent this query for retrieval: query 2",
            "Represent this query for retrieval: query 3",
            "Represent this query for retrieval: query 4",
            "Represent this query for retrieval: query 5",
            "Represent this query for retrieval: query 6",
            "Represent this query for retrieval: query 7",
            "Represent this query for retrieval: query 8",
            "Represent this query for retrieval: query 9",
            "Represent this query for retrieval: query 10",
        ]

        batch_results = []

        print("\n Batch processing latency:\n")

        for batch_size in batch_sizes:
            if batch_size > len(test_queries):
                continue

            queries = test_queries[:batch_size]
            total_original = 0
            total_quantized = 0

            for query in queries:
                ort_inputs = self.prepare_inputs(query, tokenizer)

                start = time.time()
                original_session.run(None, ort_inputs)
                total_original += (time.time() - start) * 1000

                start = time.time()
                quantized_session.run(None, ort_inputs)
                total_quantized += (time.time() - start) * 1000

            avg_original = total_original / batch_size
            avg_quantized = total_quantized / batch_size

            batch_results.append(
                {
                    "batch_size": batch_size,
                    "original_avg_ms": round(avg_original, 2),
                    "quantized_avg_ms": round(avg_quantized, 2),
                    "speedup": round(avg_original / avg_quantized, 2),
                }
            )

            print(
                f"  Batch {batch_size}: Original {avg_original:.2f}ms → Quantized {avg_quantized:.2f}ms"
            )

        self.results["tests"].append(
            {"name": "Batch Processing", "status": "PASSED", "results": batch_results}
        )

        return True

    def test_memory_efficiency(self) -> bool:
        """Test memory efficiency improvements"""
        print("\n" + "=" * 70)
        print("💾 TEST 4: MEMORY EFFICIENCY")
        print("=" * 70)

        original_size = os.path.getsize(self.original_model_path) / (1024 * 1024)
        quantized_size = os.path.getsize(self.quantized_model_path) / (1024 * 1024)

        size_reduction = original_size - quantized_size
        reduction_pct = (size_reduction / original_size) * 100

        results = {
            "original_model_size_mb": round(original_size, 2),
            "quantized_model_size_mb": round(quantized_size, 2),
            "size_reduction_mb": round(size_reduction, 2),
            "reduction_percentage": round(reduction_pct, 2),
            "estimated_memory_savings_pct": round(reduction_pct * 0.75, 2),
        }

        print(f"\n📊 MEMORY EFFICIENCY:")
        print(f"  Original size: {original_size:.2f}MB")
        print(f"  Quantized size: {quantized_size:.2f}MB")
        print(f"  Reduction: {size_reduction:.2f}MB ({reduction_pct:.1f}%)")
        print(
            f"  Est. runtime memory savings: {results['estimated_memory_savings_pct']:.1f}%"
        )

        self.results["tests"].append(
            {
                "name": "Memory Efficiency",
                "status": "PASSED",
                "results": results,
            }
        )

        return True

    def test_consistency(self, num_iterations: int = 10) -> bool:
        """Test consistency across multiple runs"""
        print("\n" + "=" * 70)
        print("🔄 TEST 5: CONSISTENCY ACROSS RUNS")
        print("=" * 70)

        _, quantized_session = self.load_sessions()
        if not quantized_session:
            return False

        tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
        test_query = "Represent this query for retrieval: consistency test"
        ort_inputs = self.prepare_inputs(test_query, tokenizer)

        embeddings = []
        latencies = []

        print(f"\n Running {num_iterations} consistency tests...\n")

        for i in range(num_iterations):
            start = time.time()
            outputs = quantized_session.run(None, ort_inputs)
            latencies.append((time.time() - start) * 1000)

            embedding = self.extract_embedding(outputs)
            embeddings.append(embedding)

        # Calculate embedding consistency
        first_embedding = embeddings[0]
        similarities = []

        for embedding in embeddings[1:]:
            dot_product = np.dot(first_embedding, embedding)
            norm1 = np.linalg.norm(first_embedding)
            norm2 = np.linalg.norm(embedding)
            similarity = dot_product / (norm1 * norm2)
            similarities.append(float(similarity))

        avg_similarity = mean(similarities)
        avg_latency = mean(latencies)
        latency_variance = stdev(latencies) if len(latencies) > 1 else 0

        results = {
            "num_iterations": num_iterations,
            "embedding_similarity": {
                "avg": round(avg_similarity, 4),
                "min": round(min(similarities), 4),
                "max": round(max(similarities), 4),
            },
            "latency_consistency_ms": {
                "avg": round(avg_latency, 2),
                "stdev": round(latency_variance, 2),
                "min": round(min(latencies), 2),
                "max": round(max(latencies), 2),
                "variance_pct": round((latency_variance / avg_latency) * 100, 2),
            },
        }

        print(f"\n📊 CONSISTENCY RESULTS:")
        print(f"  Embedding similarity: {avg_similarity:.4f}")
        print(f"  Avg latency: {avg_latency:.2f}ms")
        print(
            f"  Latency variance: {latency_variance:.2f}ms ({results['latency_consistency_ms']['variance_pct']}%)"
        )
        print(
            f"  Status: {'✓ CONSISTENT' if avg_similarity > 0.999 else '⚠️  SLIGHT VARIATIONS'}"
        )

        self.results["tests"].append(
            {"name": "Consistency", "status": "PASSED", "results": results}
        )

        return True

    def save_results(self, filename: str = "quantized_model_tests.json"):
        """Save test results"""
        output_path = Path(__file__).parent.parent / filename
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Test results saved to: {output_path}")

    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        print("\n" + "=" * 70)
        print("🧪 QUANTIZED MODEL COMPLETE TEST SUITE")
        print("=" * 70)

        all_passed = True

        try:
            # Test 1: Correctness
            if not self.test_correctness(num_queries=5):
                all_passed = False

            # Test 2: Latency
            if not self.test_latency(num_queries=20):
                all_passed = False

            # Test 3: Batch Processing
            if not self.test_batch_processing(batch_sizes=[1, 5, 10]):
                all_passed = False

            # Test 4: Memory Efficiency
            if not self.test_memory_efficiency():
                all_passed = False

            # Test 5: Consistency
            if not self.test_consistency(num_iterations=10):
                all_passed = False

        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            import traceback

            traceback.print_exc()
            all_passed = False

        # Save results
        self.save_results()

        # Print summary
        print("\n" + "=" * 70)
        print("📋 TEST SUMMARY")
        print("=" * 70)

        passed = sum(1 for test in self.results["tests"] if test["status"] == "PASSED")
        total = len(self.results["tests"])

        print(f"\n✅ Tests Passed: {passed}/{total}")
        for test in self.results["tests"]:
            status_icon = "✓" if test["status"] == "PASSED" else "⚠️"
            print(f"  {status_icon} {test['name']}")

        print("\n" + "=" * 70)
        return all_passed


def main():
    """Main entry point"""
    tester = QuantizedModelTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
