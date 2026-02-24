#!/bin/bash
# Script para descargar 2000 películas en el servidor

set -e

echo "📊 Iniciando descarga de 2000 películas TMDB en servidor..."

# Parámetros
SERVER="root@194.164.207.6"
REMOTE_DIR="/var/www/readyapi"

# 1. Enviar script de descarga
echo "1️⃣ Enviando script get_data_TMDB.py al servidor..."
scp /Users/estebanbardolet/Desktop/API_IA/scripts/get_data_TMDB.py "$SERVER:$REMOTE_DIR/scripts/"

# 2. Ejecutar descarga en servidor
echo "2️⃣ Descargando 2000 películas desde TMDB (esto toma ~5-10 minutos)..."
ssh -t "$SERVER" "cd $REMOTE_DIR/scripts && source ../venv/bin/activate && timeout 600 python3 get_data_TMDB.py"

# 3. Copiar resultado a /data
echo "3️⃣ Moviendo dataset a /data..."
ssh "$SERVER" "mv $REMOTE_DIR/scripts/tmdb_2000_movies.json $REMOTE_DIR/data/"

# 4. Cargar en ChromaDB
echo "4️⃣ Cargando 2000 películas en ChromaDB..."
ssh -t "$SERVER" "cd $REMOTE_DIR && source venv/bin/activate && python3 scripts/load_documents.py --file data/tmdb_2000_movies.json --clear --tenant admin"

# 5. Reiniciar servicio
echo "5️⃣ Reiniciando servicio..."
ssh "$SERVER" "systemctl restart readyapi"

echo "✅ ¡Listo! 2000 películas cargadas en el servidor"
