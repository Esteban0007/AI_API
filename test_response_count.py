#!/usr/bin/env python3
"""
Test API response count - verificar si devuelve el número correcto de resultados
"""

import requests
import json
import sys

API_URL = "https://api.readyapi.net/api/v1/search/query"
API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"

print("\n" + "=" * 80)
print("TEST: Verificar número de resultados devueltos")
print("=" * 80 + "\n")

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Test con diferentes valores de top_k
test_cases = [1, 3, 5, 10, 15]

for top_k in test_cases:
    query = "movies about science fiction"

    try:
        response = requests.post(
            API_URL, json={"query": query, "top_k": top_k}, headers=headers, timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Verificar estructura de respuesta
            if "results" in data:
                num_results = len(data["results"])
                print(
                    f"✓ top_k={top_k:2}  →  Recibidos: {num_results:2} resultados",
                    end="",
                )

                if num_results == top_k:
                    print("  ✅ CORRECTO")
                elif num_results < top_k:
                    print(f"  ⚠️  MENOS (esperado {top_k})")
                else:
                    print(f"  ⚠️  MÁS (esperado {top_k})")

                # Mostrar estructura de datos
                if num_results > 0:
                    print(
                        f"   Ejemplo resultado: {json.dumps(data['results'][0], indent=2)[:200]}..."
                    )

            elif "details" in data:
                num_results = len(data["details"])
                print(
                    f"✓ top_k={top_k:2}  →  Recibidos: {num_results:2} en 'details'",
                    end="",
                )
                if num_results == top_k:
                    print("  ✅")
                else:
                    print(f"  ⚠️ (esperado {top_k})")
            else:
                print(
                    f"✗ top_k={top_k:2}  →  Estructura desconocida: {list(data.keys())}"
                )
                print(f"   Response: {json.dumps(data, indent=2)[:300]}")
        else:
            print(f"✗ top_k={top_k:2}  →  HTTP {response.status_code}")
            print(f"   Error: {response.text[:200]}")

    except Exception as e:
        print(f"✗ top_k={top_k:2}  →  Error: {str(e)}")

print("\n" + "=" * 80)
print("ANÁLISIS")
print("=" * 80 + "\n")

# Verificar una respuesta completa
print("Ejemplo de respuesta completa (top_k=5):\n")
try:
    response = requests.post(
        API_URL, json={"query": "Avatar", "top_k": 5}, headers=headers, timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2)[:1000])
    else:
        print(f"Error: {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
