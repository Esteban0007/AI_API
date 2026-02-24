#!/bin/bash
# Script para descargar 2000 películas en background en servidor

SERVER="root@194.164.207.6"
REMOTE_DIR="/var/www/readyapi"

echo "📊 Iniciando descarga de 2000 películas en servidor..."
echo "ℹ️  El proceso se ejecuta en background. Puedes verificar con: tail -f /var/www/readyapi/download.log"

ssh "$SERVER" << 'SSHSCRIPT'
cd /var/www/readyapi

# Crear log
exec > >(tee -a download.log)
exec 2>&1

echo "$(date): Iniciando descarga TMDB..."

# Descargar (esto toma tiempo)
source venv/bin/activate
timeout 600 python3 scripts/get_data_TMDB.py

# Si la descarga fue exitosa, mover archivo
if [ -f scripts/tmdb_2000_movies.json ]; then
    echo "$(date): Moviendo dataset a /data..."
    mv scripts/tmdb_2000_movies.json data/
    
    echo "$(date): Cargando en ChromaDB..."
    python3 scripts/load_documents.py --file data/tmdb_2000_movies.json --clear --tenant admin
    
    echo "$(date): Reiniciando servicio..."
    systemctl restart readyapi
    
    echo "$(date): ✅ ¡LISTO! 2000 películas cargadas"
else
    echo "$(date): ❌ Error: No se pudo descargar el dataset"
fi

SSHSCRIPT &

echo "✅ Proceso iniciado en background en servidor"
echo "ℹ️  Usa: ssh root@194.164.207.6 'tail -f /var/www/readyapi/download.log' para monitorear"
