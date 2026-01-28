#!/bin/bash
# 🚀 Quick Start Script for Semantic Search SaaS

set -e

echo "════════════════════════════════════════════════════════════"
echo "  Semantic Search SaaS - Quick Start Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip -q

# Install requirements
echo "✓ Installing dependencies..."
echo "  (This may take a few minutes on first run...)"
pip install -r requirements.txt -q

# Create data directory
echo "✓ Creating data directory..."
mkdir -p data

# Run tests
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Running Installation Tests"
echo "════════════════════════════════════════════════════════════"
python tests/test_example.py

# Generate sample data
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Generating Sample Data"
echo "════════════════════════════════════════════════════════════"
python scripts/create_sample_data.py

# Load sample data
echo ""
echo "✓ Loading sample documents into vector database..."
python scripts/load_json.py data/sample_documents.json

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ Setup Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Start the server:"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  2. Open in browser:"
echo "     http://localhost:8000/api/docs"
echo ""
echo "  3. Try a search query (POST /api/v1/search/query):"
echo "     {\"query\": \"machine learning\", \"top_k\": 5}"
echo ""
echo "Documentation:"
echo "  • Quick Start:  QUICKSTART.md"
echo "  • Full Setup:   SETUP.md"
echo "  • Full Docs:    README.md"
echo "  • Deployment:   DEPLOYMENT.md"
echo ""
echo "════════════════════════════════════════════════════════════"
