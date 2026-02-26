#!/usr/bin/env python3
"""
INT8 Quantization for Arctic ONNX Model
Reduces model size and CPU memory usage while maintaining performance
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from statistics import mean, stdev

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from onnxruntime.quantization import quantize_dynamic, QuantType
    from onnxruntime.quantization.onnx_model_utils import (
        load_model_initializers_for_ort,
    )
except ImportError:
    print("Installing onnxruntime with quantization support...")
    os.system("pip install --upgrade onnxruntime[tools]")
    from onnxruntime.quantization import quantize_dynamic, QuantType

import numpy as np
from transformers import AutoTokenizer


class ArcticQuantizer:
    """Handles INT8 quantization of Arctic ONNX model"""

    def __init__(self, model_dir: str = "/var/www/readyapi/models/arctic_onnx"):
        """
        Initialize quantizer

        Args:
            model_dir: Directory containing Arctic ONNX model
        """
        self.model_dir = model_dir
        self.model_path = f"{model_dir}/model.onnx"
        self.quantized_model_path = f"{model_dir}/model_int8.onnx"
        self.tokenizer_path = model_dir
        self.quantization_results = {
            "timestamp": datetime.now().isoformat(),
            "model_dir": model_dir,
            "steps": [],
        }

    def log_step(self, step_name: str, details: dict):
        """Log a quantization step"""
        self.quantization_results["steps"].append(
            {
                "step": step_name,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"✓ {step_name}: {details}")

    def check_model_exists(self) -> bool:
        """Verify model files exist"""
        if not os.path.exists(self.model_path):
            print(f"❌ Model not found at: {self.model_path}")
            return False
        if not os.path.exists(self.tokenizer_path):
            print(f"⚠️  Tokenizer not found at: {self.tokenizer_path}")
        return True

    def get_model_size(self, path: str) -> dict:
        """Get model file size info"""
        if not os.path.exists(path):
            return {"exists": False, "size_mb": 0}

        size_bytes = os.path.getsize(path)
        size_mb = size_bytes / (1024 * 1024)
        return {"exists": True, "size_bytes": size_bytes, "size_mb": round(size_mb, 2)}

    def quantize_model(self) -> bool:
        """
        Perform INT8 quantization using dynamic quantization
        (Doesn't require calibration data)
        """
        print("\n" + "=" * 70)
        print("🔄 ARCTIC INT8 QUANTIZATION")
        print("=" * 70)

        try:
            print(f"\n📁 Model directory: {self.model_dir}")
            print(f"📄 Input model: {self.model_path}")
            print(f"💾 Output model: {self.quantized_model_path}")

            # Verify model exists
            if not self.check_model_exists():
                return False

            # Get original size
            original_size = self.get_model_size(self.model_path)
            print(
                f"\n📊 Original model size: {original_size['size_mb']}MB ({original_size['size_bytes']:,} bytes)"
            )
            self.log_step(
                "Model size check", {"original_size_mb": original_size["size_mb"]}
            )

            # Perform quantization
            print("\n⚙️  Applying INT8 dynamic quantization...")
            start_time = time.time()

            # Use only compatible parameters for onnxruntime 1.24.2
            quantize_dynamic(
                self.model_path,
                self.quantized_model_path,
                weight_type=QuantType.QInt8,
            )

            quantization_time = (time.time() - start_time) * 1000
            self.log_step(
                "INT8 dynamic quantization", {"time_ms": round(quantization_time, 2)}
            )
            print(f"✓ Quantization completed in {quantization_time:.2f}ms")

            # Get quantized size
            quantized_size = self.get_model_size(self.quantized_model_path)
            if not quantized_size["exists"]:
                print("❌ Quantized model not created")
                return False

            print(
                f"📊 Quantized model size: {quantized_size['size_mb']}MB ({quantized_size['size_bytes']:,} bytes)"
            )

            # Calculate reduction
            size_reduction = original_size["size_mb"] - quantized_size["size_mb"]
            size_reduction_pct = (size_reduction / original_size["size_mb"]) * 100

            self.log_step(
                "Size comparison",
                {
                    "original_mb": original_size["size_mb"],
                    "quantized_mb": quantized_size["size_mb"],
                    "reduction_mb": round(size_reduction, 2),
                    "reduction_pct": round(size_reduction_pct, 2),
                },
            )

            print(
                f"\n📉 Size reduction: {size_reduction:.2f}MB ({size_reduction_pct:.1f}%)"
            )

            return True

        except Exception as e:
            print(f"❌ Quantization failed: {e}")
            self.log_step("Quantization error", {"error": str(e)})
            import traceback

            traceback.print_exc()
            return False

    def verify_quantized_model(self) -> bool:
        """Verify quantized model can be loaded and used"""
        print("\n" + "=" * 70)
        print("✅ VERIFICATION: Loading Quantized Model")
        print("=" * 70)

        try:
            import onnxruntime as ort

            print("\n🔍 Loading quantized model...")
            start_time = time.time()

            session = ort.InferenceSession(
                self.quantized_model_path, providers=["CPUExecutionProvider"]
            )

            load_time = (time.time() - start_time) * 1000
            print(f"✓ Model loaded in {load_time:.2f}ms")
            self.log_step("Model load time", {"load_time_ms": round(load_time, 2)})

            # Get model info
            input_names = [i.name for i in session.get_inputs()]
            output_names = [o.name for o in session.get_outputs()]

            print(f"\n📋 Model inputs: {input_names}")
            print(f"📋 Model outputs: {output_names}")

            self.log_step(
                "Model info", {"inputs": input_names, "outputs": output_names}
            )

            # Test with dummy data
            print("\n🧪 Testing with dummy data...")
            tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)
            test_text = "Represent this query for retrieval: test query"

            tokens = tokenizer(
                test_text,
                max_length=512,
                padding="max_length",
                truncation=True,
                return_tensors="np",
            )

            # Prepare inputs
            ort_inputs = {
                "input_ids": tokens["input_ids"].astype(np.int64),
                "attention_mask": tokens["attention_mask"].astype(np.int64),
            }

            # Add token_type_ids if present in original model
            if "token_type_ids" in tokens:
                ort_inputs["token_type_ids"] = tokens["token_type_ids"].astype(np.int64)

            # Run inference
            start_time = time.time()
            outputs = session.run(None, ort_inputs)
            inference_time = (time.time() - start_time) * 1000

            print(f"✓ Inference successful in {inference_time:.2f}ms")
            print(f"✓ Output shape: {outputs[0].shape}")
            self.log_step(
                "Inference test",
                {
                    "time_ms": round(inference_time, 2),
                    "output_shape": str(outputs[0].shape),
                },
            )

            return True

        except Exception as e:
            print(f"❌ Verification failed: {e}")
            self.log_step("Verification error", {"error": str(e)})
            import traceback

            traceback.print_exc()
            return False

    def benchmark_quantized_vs_original(self, num_queries: int = 10) -> dict:
        """
        Benchmark quantized model vs original
        Requires API access to test full pipeline
        """
        print("\n" + "=" * 70)
        print("⚡ BENCHMARK: Quantized vs Original Model")
        print("=" * 70)

        import onnxruntime as ort

        try:
            # Load both models
            print("\n📂 Loading models...")
            original_session = ort.InferenceSession(
                self.model_path, providers=["CPUExecutionProvider"]
            )
            quantized_session = ort.InferenceSession(
                self.quantized_model_path, providers=["CPUExecutionProvider"]
            )

            tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)

            # Test queries
            test_queries = [
                "Represent this query for retrieval: Christopher Nolan movies",
                "Represent this query for retrieval: science fiction films",
                "Represent this query for retrieval: action adventure",
                "Represent this query for retrieval: drama romance",
                "Represent this query for retrieval: thriller mystery",
            ]

            # Use fewer queries if requested
            test_queries = test_queries[:num_queries]

            results = {
                "num_queries": len(test_queries),
                "queries": [],
                "original_model": {
                    "total_ms": 0,
                    "avg_ms": 0,
                    "min_ms": 0,
                    "max_ms": 0,
                },
                "quantized_model": {
                    "total_ms": 0,
                    "avg_ms": 0,
                    "min_ms": 0,
                    "max_ms": 0,
                },
                "speedup": 0,
                "memory_savings_pct": 0,
            }

            print(f"\n🧪 Running {len(test_queries)} benchmark queries...\n")

            for i, query in enumerate(test_queries, 1):
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
                    ort_inputs["token_type_ids"] = tokens["token_type_ids"].astype(
                        np.int64
                    )

                # Benchmark original
                start = time.time()
                original_session.run(None, ort_inputs)
                original_time = (time.time() - start) * 1000

                # Benchmark quantized
                start = time.time()
                quantized_session.run(None, ort_inputs)
                quantized_time = (time.time() - start) * 1000

                results["queries"].append(
                    {
                        "query_num": i,
                        "original_ms": round(original_time, 2),
                        "quantized_ms": round(quantized_time, 2),
                    }
                )

                results["original_model"]["total_ms"] += original_time
                results["quantized_model"]["total_ms"] += quantized_time

                print(
                    f"  Query {i}: Original {original_time:.2f}ms → Quantized {quantized_time:.2f}ms"
                )

            # Calculate averages
            n = len(test_queries)
            results["original_model"]["avg_ms"] = round(
                results["original_model"]["total_ms"] / n, 2
            )
            results["quantized_model"]["avg_ms"] = round(
                results["quantized_model"]["total_ms"] / n, 2
            )

            original_times = [q["original_ms"] for q in results["queries"]]
            quantized_times = [q["quantized_ms"] for q in results["queries"]]

            results["original_model"]["min_ms"] = min(original_times)
            results["original_model"]["max_ms"] = max(original_times)
            results["quantized_model"]["min_ms"] = min(quantized_times)
            results["quantized_model"]["max_ms"] = max(quantized_times)

            # Calculate speedup
            speedup = (
                results["original_model"]["avg_ms"]
                / results["quantized_model"]["avg_ms"]
            )
            results["speedup"] = round(speedup, 2)

            # Calculate memory savings
            original_size_mb = self.get_model_size(self.model_path)["size_mb"]
            quantized_size_mb = self.get_model_size(self.quantized_model_path)[
                "size_mb"
            ]
            memory_savings = (
                (original_size_mb - quantized_size_mb) / original_size_mb
            ) * 100
            results["memory_savings_pct"] = round(memory_savings, 2)

            print(f"\n📊 BENCHMARK RESULTS:")
            print(f"  Original avg: {results['original_model']['avg_ms']}ms")
            print(f"  Quantized avg: {results['quantized_model']['avg_ms']}ms")
            print(f"  Speedup: {results['speedup']}x")
            print(f"  Memory saved: {results['memory_savings_pct']}%")

            self.log_step(
                "Benchmark comparison",
                {
                    "original_avg_ms": results["original_model"]["avg_ms"],
                    "quantized_avg_ms": results["quantized_model"]["avg_ms"],
                    "speedup": results["speedup"],
                    "memory_savings_pct": results["memory_savings_pct"],
                },
            )

            return results

        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            import traceback

            traceback.print_exc()
            return None

    def save_results(self, filename: str = "quantization_results.json"):
        """Save quantization results to file"""
        output_path = f"/Users/estebanbardolet/Desktop/API_IA/{filename}"
        with open(output_path, "w") as f:
            json.dump(self.quantization_results, f, indent=2)
        print(f"\n✅ Results saved to: {output_path}")

    def run_full_pipeline(self) -> bool:
        """Execute complete quantization pipeline"""
        print("\n" + "=" * 70)
        print("🚀 ARCTIC ONNX INT8 QUANTIZATION - FULL PIPELINE")
        print("=" * 70)

        # Step 1: Quantize
        if not self.quantize_model():
            return False

        # Step 2: Verify
        if not self.verify_quantized_model():
            return False

        # Step 3: Benchmark
        benchmark_results = self.benchmark_quantized_vs_original(num_queries=10)
        if benchmark_results:
            self.quantization_results["benchmark"] = benchmark_results

        # Save results
        self.save_results()

        print("\n" + "=" * 70)
        print("✅ QUANTIZATION COMPLETE")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"  ✓ Model quantized: {self.quantized_model_path}")
        print(
            f"  ✓ Size reduction: {self.quantization_results['steps'][2]['details']['reduction_pct']}%"
        )
        if benchmark_results:
            print(f"  ✓ Speedup: {benchmark_results['speedup']}x")
            print(f"  ✓ Memory saved: {benchmark_results['memory_savings_pct']}%")

        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Quantize Arctic ONNX model to INT8")
    parser.add_argument(
        "--model-dir",
        default="/var/www/readyapi/models/arctic_onnx",
        help="Directory containing Arctic ONNX model",
    )
    parser.add_argument(
        "--benchmark-queries",
        type=int,
        default=10,
        help="Number of queries for benchmarking",
    )
    parser.add_argument(
        "--output", default="quantization_results.json", help="Output results file"
    )

    args = parser.parse_args()

    quantizer = ArcticQuantizer(model_dir=args.model_dir)
    quantizer.run_full_pipeline()


if __name__ == "__main__":
    main()
