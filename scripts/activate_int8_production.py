#!/usr/bin/env python3
"""
Activate INT8 quantization in production
Generates the INT8 quantized model from the standard ONNX model
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def activate_int8_quantization():
    """Generate INT8 quantized model from standard ONNX model"""

    print("\n" + "=" * 80)
    print("INT8 QUANTIZATION ACTIVATION - Production Setup")
    print("=" * 80)

    # Check if quantization script exists
    quantize_script = Path(__file__).parent / "quantize_arctic_int8.py"
    if not quantize_script.exists():
        print(f"❌ Quantization script not found: {quantize_script}")
        return False

    print("\n📦 Running quantization process...")
    os.system(f"python3 {quantize_script}")

    # Verify INT8 model was created
    from app.core.config import get_settings

    settings = get_settings()

    onnx_dir = settings.EMBEDDING_ONNX_DIR
    if not onnx_dir:
        print("❌ EMBEDDING_ONNX_DIR not configured")
        return False

    int8_model = Path(onnx_dir) / "model_int8.onnx"
    if int8_model.exists():
        size_mb = int8_model.stat().st_size / (1024 * 1024)
        print(f"\n✅ INT8 model created successfully")
        print(f"   Location: {int8_model}")
        print(f"   Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ INT8 model not found at {int8_model}")
        return False


def test_int8_embeddings():
    """Test INT8 quantized embeddings"""

    print("\n" + "=" * 80)
    print("Testing INT8 Embeddings")
    print("=" * 80 + "\n")

    from app.engine.embedder import Embedder
    from app.core.config import get_settings

    settings = get_settings()
    settings.EMBEDDING_USE_ONNX = True
    settings.EMBEDDING_USE_INT8_QUANTIZATION = True

    if not settings.EMBEDDING_ONNX_DIR:
        print("❌ EMBEDDING_ONNX_DIR not configured")
        return False

    try:
        embedder = Embedder()

        # Check if INT8 is loaded
        if not embedder.is_int8_quantized():
            print("⚠️  INT8 quantization not loaded")
            print("   Standard ONNX model is being used")
            return False

        print("✅ INT8 quantized model loaded successfully")

        # Test embedding generation
        test_queries = [
            "movies about artificial intelligence",
            "space exploration science fiction",
            "time travel paradox",
        ]

        print("\n🧪 Running test embeddings...")
        for i, query in enumerate(test_queries, 1):
            start = time.time()
            embedding = embedder.embed_query(query)
            latency = (time.time() - start) * 1000

            print(
                f"   {i}. {query[:40]:40} -> {latency:7.1f}ms (dim: {len(embedding)})"
            )

        print("\n✅ INT8 embedding tests passed")
        return True

    except Exception as e:
        print(f"❌ Error testing INT8 embeddings: {e}")
        return False


def print_status():
    """Print current INT8 status"""

    print("\n" + "=" * 80)
    print("INT8 Quantization Status")
    print("=" * 80 + "\n")

    from app.core.config import get_settings

    settings = get_settings()

    print(f"EMBEDDING_USE_ONNX: {settings.EMBEDDING_USE_ONNX}")
    print(
        f"EMBEDDING_USE_INT8_QUANTIZATION: {settings.EMBEDDING_USE_INT8_QUANTIZATION}"
    )
    print(f"EMBEDDING_ONNX_DIR: {settings.EMBEDDING_ONNX_DIR}")

    if settings.EMBEDDING_ONNX_DIR:
        onnx_dir = Path(settings.EMBEDDING_ONNX_DIR)
        standard_model = onnx_dir / "model.onnx"
        int8_model = onnx_dir / "model_int8.onnx"

        print(f"\nModel Files:")
        if standard_model.exists():
            size = standard_model.stat().st_size / (1024**3)
            print(f"  ✓ Standard ONNX: {size:.2f} GB")
        else:
            print(f"  ✗ Standard ONNX: not found")

        if int8_model.exists():
            size = int8_model.stat().st_size / (1024**2)
            print(f"  ✓ INT8 ONNX: {size:.1f} MB (75% smaller)")
        else:
            print(f"  ✗ INT8 ONNX: not found")


if __name__ == "__main__":
    print_status()

    # Check for INT8 model
    from app.core.config import get_settings

    settings = get_settings()

    if settings.EMBEDDING_ONNX_DIR:
        int8_model = Path(settings.EMBEDDING_ONNX_DIR) / "model_int8.onnx"

        if not int8_model.exists():
            print("\n" + "=" * 80)
            print("INT8 Model Not Found - Generating...")
            print("=" * 80)
            if activate_int8_quantization():
                test_int8_embeddings()
        else:
            print(f"\n✅ INT8 model already exists")
            test_int8_embeddings()
    else:
        print("\n⚠️  EMBEDDING_ONNX_DIR not configured")
        print("   Please set EMBEDDING_ONNX_DIR in environment or config")
