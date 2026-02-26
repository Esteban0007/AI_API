#!/usr/bin/env python3
"""
Test exhaustivo - Ver exactamente qué está devolviendo el API
"""

import requests
import json

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

print("\n" + "=" * 80)
print("RESPUESTA COMPLETA DEL API - top_k=5")
print("=" * 80 + "\n")

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

response = requests.post(API_URL, json={"query": "movies", "top_k": 5}, headers=headers)

data = response.json()

print(f"Query: {data.get('query')}")
print(f"Total Results (según API): {data.get('total_results')}")
print(f"Número de items en 'results': {len(data.get('results', []))}")
print(f"\nRespuesta completa:")
print(json.dumps(data, indent=2)[:2000])

print("\n" + "=" * 80)
print("ANÁLISIS")
print("=" * 80)

results = data.get("results", [])
if len(results) == 5:
    print("✅ El API está devolviendo correctamente 5 resultados")
elif len(results) < 5:
    print(f"⚠️ El API está devolviendo solo {len(results)} resultados (esperado 5)")
    print("   POSIBLE CAUSA: No hay suficientes documentos en la base de datos")
elif len(results) > 5:
    print(f"❌ El API está devolviendo {len(results)} resultados (esperado 5)")
    print("   PROBLEMA: El API está devolviendo más de lo solicitado")

print("\n")
print("Detalles de cada resultado:")
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result.get('title')} (ID: {result.get('id')})")
    print(f"   Score: {result.get('score')}")
