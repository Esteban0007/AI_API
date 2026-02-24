#!/usr/bin/env python3
"""Limpiar dataset TMDB removiendo duplicados."""

import json
import sys


def clean_tmdb_dataset(input_file, output_file):
    print(f"📖 Leyendo {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = data["documents"]
    print(f"Total documentos antes: {len(documents)}")

    # Usar dict para mantener solo IDs únicas (último gana)
    unique_docs = {}
    for doc in documents:
        doc_id = doc.get("id")
        if doc_id:
            if doc_id in unique_docs:
                print(f"⚠️  Duplicado encontrado: {doc_id}")
            unique_docs[doc_id] = doc

    cleaned_docs = list(unique_docs.values())
    print(f"Total documentos después: {len(cleaned_docs)}")
    print(f"Duplicados removidos: {len(documents) - len(cleaned_docs)}")

    # Guardar
    output_data = {"documents": cleaned_docs}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Guardado en {output_file}")


if __name__ == "__main__":
    clean_tmdb_dataset(
        "/var/www/readyapi/tmdb_2000_movies.json",
        "/var/www/readyapi/data/tmdb_clean.json",
    )
