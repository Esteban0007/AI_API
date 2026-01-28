#!/usr/bin/env python
"""
Quick test script for the semantic search API.
"""
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from app.core.config import get_settings

settings = get_settings()

BASE_URL = f"http://localhost:{settings.PORT}/api/v1"


def test_upload_documents():
    """Test document upload endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Upload Documents")
    print("="*60)
    
    documents = {
        "documents": [
            {
                "id": "test-001",
                "title": "Python Basics",
                "content": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms and has a comprehensive standard library.",
                "keywords": ["python", "programming"],
                "metadata": {
                    "category": "programming",
                    "language": "en"
                }
            },
            {
                "id": "test-002",
                "title": "Web Development with FastAPI",
                "content": "FastAPI is a modern web framework for building APIs with Python. It's built on top of Starlette and Pydantic, providing excellent performance and automatic API documentation.",
                "keywords": ["fastapi", "web"],
                "metadata": {
                    "category": "web",
                    "language": "en"
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/documents/upload",
            json=documents,
            headers={"X-API-Key": "dev-key"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_search():
    """Test search endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Semantic Search")
    print("="*60)
    
    query = {
        "query": "Python programming language",
        "top_k": 5,
        "include_content": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/search/query",
            json=query,
            headers={"X-API-Key": "dev-key"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_stats():
    """Test collection statistics endpoint."""
    print("\n" + "="*60)
    print("TEST 3: Collection Statistics")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/stats",
            headers={"X-API-Key": "dev-key"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_health():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TEST 4: Health Check")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/search/health",
            headers={"X-API-Key": "dev-key"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🚀 "*20)
    print("SEMANTIC SEARCH API - TEST SUITE")
    print("🚀 "*20)
    
    print(f"\nConnecting to: {BASE_URL}")
    
    # Run tests
    results = {
        "Upload Documents": test_upload_documents(),
        "Search": test_search(),
        "Statistics": test_stats(),
        "Health Check": test_health()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")


if __name__ == "__main__":
    main()
