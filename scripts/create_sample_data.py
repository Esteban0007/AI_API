"""
Example data file for testing.
"""
import json

# Create sample documents
sample_documents = [
    {
        "id": "doc-001",
        "title": "Introducción a Machine Learning",
        "content": "Machine Learning es una rama de la inteligencia artificial que permite a las máquinas aprender de los datos sin ser programadas explícitamente. Los algoritmos de aprendizaje automático pueden identificar patrones en los datos y hacer predicciones basadas en esos patrones. Esto es diferente a la programación tradicional donde especificas cada regla que la máquina debe seguir.",
        "keywords": ["machine-learning", "ai", "algorithms", "learning"],
        "metadata": {
            "category": "tutorial",
            "language": "es",
            "source": "https://example.com/ml-intro"
        }
    },
    {
        "id": "doc-002",
        "title": "Redes Neuronales Profundas",
        "content": "Las redes neuronales profundas son modelos inspirados en el funcionamiento del cerebro humano. Consisten en capas de neuronas artificiales conectadas entre sí que procesan información. El aprendizaje profundo ha revolucionado campos como la visión por computadora, procesamiento de lenguaje natural y reconocimiento de voz.",
        "keywords": ["neural-networks", "deep-learning", "ai"],
        "metadata": {
            "category": "advanced",
            "language": "es",
            "source": "https://example.com/neural-networks"
        }
    },
    {
        "id": "doc-003",
        "title": "Procesamiento de Lenguaje Natural",
        "content": "El Procesamiento de Lenguaje Natural (NLP) es un campo de la inteligencia artificial que se enfoca en la interacción entre computadoras y lenguaje humano. Permite a las máquinas entender, interpretar y generar texto de manera similar a como lo hacen los humanos. Los transformers y modelos como BERT han revolucionado este campo.",
        "keywords": ["nlp", "language", "text-processing", "transformers"],
        "metadata": {
            "category": "nlp",
            "language": "es",
            "source": "https://example.com/nlp-intro"
        }
    },
    {
        "id": "doc-004",
        "title": "Visión por Computadora",
        "content": "La Visión por Computadora es la disciplina que permite a las máquinas interpretar y entender imágenes digitales. Utiliza algoritmos de procesamiento de imágenes y aprendizaje profundo para reconocer objetos, detectar características y analizar contenido visual. Aplicaciones incluyen reconocimiento facial, conducción autónoma y diagnóstico médico.",
        "keywords": ["computer-vision", "image-processing", "deep-learning"],
        "metadata": {
            "category": "computer-vision",
            "language": "es",
            "source": "https://example.com/vision-intro"
        }
    },
    {
        "id": "doc-005",
        "title": "Sistemas de Recomendación",
        "content": "Los sistemas de recomendación son algoritmos que predicen las preferencias de los usuarios y sugieren items relevantes. Existen tres enfoques principales: filtrado colaborativo, filtrado basado en contenido e híbridos. Estos sistemas son fundamentales en plataformas de comercio electrónico, streaming de video y redes sociales.",
        "keywords": ["recommendation-systems", "collaborative-filtering", "algorithms"],
        "metadata": {
            "category": "machine-learning",
            "language": "es",
            "source": "https://example.com/recommendation"
        }
    }
]

# Save to file
with open("data/sample_documents.json", "w", encoding="utf-8") as f:
    json.dump(sample_documents, f, ensure_ascii=False, indent=2)

print(f"✅ Sample documents created: data/sample_documents.json")
print(f"   Total documents: {len(sample_documents)}")
