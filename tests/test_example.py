"""
Simple test example to verify the installation.

Run with: python tests/test_example.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.engine.embedder import Embedder
from app.engine.store import VectorStore
from app.engine.searcher import SearchEngine


def test_embedder():
    """Test embedding generation."""
    print("Testing Embedder...")
    try:
        embedder = Embedder()
        text = "This is a test document."
        embedding = embedder.embed_text(text)
        
        assert embedding.shape[0] == embedder.get_embedding_dimension()
        print(f"✅ Embedder working. Shape: {embedding.shape}")
        return True
    except Exception as e:
        print(f"❌ Embedder test failed: {e}")
        return False


def test_store():
    """Test vector storage."""
    print("\nTesting VectorStore...")
    try:
        embedder = Embedder()
        store = VectorStore(embedder=embedder)
        
        # Add a test document
        success = store.add_document(
            doc_id="test-001",
            content="This is a test document for vector storage.",
            metadata={
                "title": "Test Document",
                "category": "test"
            }
        )
        
        assert success
        print("✅ VectorStore working. Document added successfully.")
        return True
    except Exception as e:
        print(f"❌ VectorStore test failed: {e}")
        return False


def test_searcher():
    """Test search and re-ranking."""
    print("\nTesting SearchEngine...")
    try:
        embedder = Embedder()
        store = VectorStore(embedder=embedder)
        searcher = SearchEngine(vector_store=store, embedder=embedder)
        
        # Add test documents
        test_docs = [
            {
                "id": "search-test-1",
                "title": "Machine Learning Basics",
                "content": "Machine learning is a type of artificial intelligence.",
                "keywords": ["ml", "ai"],
                "metadata": {"category": "tutorial", "language": "en"}
            },
            {
                "id": "search-test-2",
                "title": "Neural Networks",
                "content": "Neural networks are inspired by biological neurons.",
                "keywords": ["neural", "deep-learning"],
                "metadata": {"category": "advanced", "language": "en"}
            }
        ]
        
        store.add_documents_batch(test_docs)
        
        # Perform search
        results, exec_time = searcher.search("How does machine learning work?", top_k=2)
        
        assert len(results) > 0
        assert "score" in results[0]
        print(f"✅ SearchEngine working. Found {len(results)} results in {exec_time:.2f}ms")
        return True
    except Exception as e:
        print(f"❌ SearchEngine test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Semantic Search SaaS - Installation Verification")
    print("=" * 60)
    
    tests = [
        test_embedder,
        test_store,
        test_searcher
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! Installation is correct.")
        print("\nNext steps:")
        print("1. python scripts/create_sample_data.py  # Create sample data")
        print("2. python scripts/load_json.py data/sample_documents.json  # Load data")
        print("3. uvicorn app.main:app --reload  # Start server")
        print("4. Open http://localhost:8000/api/docs  # View API")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("- Make sure you're in the correct directory")
        print("- Run: pip install -r requirements.txt")
        print("- Check that all dependencies are installed")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
