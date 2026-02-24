#!/bin/bash
# Script para cargar TMDB en el servidor

# 1. Crear directorio si no existe
mkdir -p /var/www/readyapi/data

# 2. Crear el dataset TMDB directamente con cat/heredoc
cat > /var/www/readyapi/data/tmdb_movies.json << 'JSON_EOF'
{
  "documents": [
    {
      "id": "tmdb-1",
      "title": "Mercy",
      "content": "A thriller about survival and redemption.",
      "keywords": ["Timur Bekmambetov", "Science Fiction", "Action", "Thriller"],
      "metadata": {
        "tmdb_id": 1,
        "language": "en",
        "original_title": "Mercy",
        "poster_path": "https://image.tmdb.org/t/p/w500/poster.jpg",
        "genres": ["Science Fiction", "Action", "Thriller"],
        "director": "Timur Bekmambetov",
        "cast": ["Actor1", "Actor2", "Actor3"],
        "release_date": "2024-01-01",
        "rating": 7.0
      }
    }
  ]
}
JSON_EOF

# 3. Cargar dataset TMDB con load_documents.py
cd /var/www/readyapi
source venv/bin/activate

echo "Loading TMDB dataset..."
python3 scripts/load_documents.py --file data/tmdb_movies.json --clear --tenant admin

echo "Done!"
