#!/usr/bin/env python3
"""
Load TMDB dataset to remote server.
"""

import subprocess
import os
import sys

local_file = "/Users/estebanbardolet/Desktop/API_IA/data/tmdb_movies.json"
remote_path = "root@194.164.207.6:/var/www/readyapi/data/tmdb_movies.json"

print("📁 Enviando dataset TMDB al servidor...")
result = subprocess.run(
    ["scp", local_file, remote_path], capture_output=True, text=True
)
if result.returncode != 0:
    print(f"❌ Error en SCP: {result.stderr}")
    sys.exit(1)

print("✅ Dataset enviado")

# Script de carga para ejecutar en servidor
load_script = """
import sys
import json
sys.path.insert(0, '/var/www/readyapi')

from app.engine.store import VectorStore
from app.engine.embedder import Embedder

with open('/var/www/readyapi/data/tmdb_movies.json') as f:
    data = json.load(f)

documents = data['documents']
print(f"Loaded {len(documents)} documents")

embedder = Embedder()
vs = VectorStore(embedder=embedder, tenant_id="admin")
vs.clear_collection()
success, fail = vs.add_documents_batch(documents)
print(f"Indexed: {success}")
"""

cmd = f"""source venv/bin/activate && cd /var/www/readyapi && python3 -c '{load_script}'"""
print("🔄 Cargando en servidor...")
result = subprocess.run(
    ["ssh", "-t", "root@194.164.207.6", cmd], capture_output=True, text=True
)
print(result.stdout)
if result.stderr:
    print(result.stderr)

print("✅ Listo!")
