#!/usr/bin/env python3
"""
Test detallado del parámetro top_k
"""

import requests
import json

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

print("\n" + "=" * 80)
print("TEST DETALLADO: top_k parameter")
print("=" * 80 + "\n")

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test 1: Sin especificar top_k (debe usar default 5)
print("TEST 1: Sin especificar top_k (debe usar default 5)")
print("-" * 80)
response = requests.post(API_URL, json={"query": "science fiction"}, headers=headers)
data = response.json()
print(f"Resultados recibidos: {len(data['results'])}")
print(f"top_k solicitado: (default) → esperado 5")
print(f"✓ CORRECTO" if len(data["results"]) == 5 else f"✗ INCORRECTO")

# Test 2: Especificando top_k=3
print("\n\nTEST 2: Especificando top_k=3")
print("-" * 80)
response = requests.post(
    API_URL, json={"query": "science fiction", "top_k": 3}, headers=headers
)
data = response.json()
print(f"Resultados recibidos: {len(data['results'])}")
print(f"top_k solicitado: 3")
print(f"✓ CORRECTO" if len(data["results"]) == 3 else f"✗ INCORRECTO")
if len(data["results"]) != 3:
    print(f"PROBLEMA: Pediste 3 pero recibiste {len(data['results'])}")

# Test 3: Especificando top_k=7
print("\n\nTEST 3: Especificando top_k=7")
print("-" * 80)
response = requests.post(
    API_URL, json={"query": "action movies", "top_k": 7}, headers=headers
)
data = response.json()
print(f"Resultados recibidos: {len(data['results'])}")
print(f"top_k solicitado: 7")
print(f"✓ CORRECTO" if len(data["results"]) == 7 else f"✗ INCORRECTO")
if len(data["results"]) != 7:
    print(f"PROBLEMA: Pediste 7 pero recibiste {len(data['results'])}")

# Test 4: Especificando top_k=5
print("\n\nTEST 4: Especificando top_k=5 explícitamente")
print("-" * 80)
response = requests.post(
    API_URL, json={"query": "thriller", "top_k": 5}, headers=headers
)
data = response.json()
print(f"Resultados recibidos: {len(data['results'])}")
print(f"top_k solicitado: 5")
print(f"✓ CORRECTO" if len(data["results"]) == 5 else f"✗ INCORRECTO")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(
    """
Si ves "✗ INCORRECTO" en alguno de los tests, significa que:
- La API no está respetando el parámetro top_k del usuario
- El servidor está forzando RERANK_TOP_K=5 en lugar de usar el valor del usuario

CAUSA PROBABLE EN searcher.py línea 109:
    final_top_k = top_k or self.rerank_top_k
    
Esto IGNORA el top_k si no se pasa, pero DEBERÍA respetarlo si se pasa.
"""
)
