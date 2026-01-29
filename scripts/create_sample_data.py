"""Generate a large, realistic medical dataset for search testing."""

import argparse
import json
import random
from datetime import datetime
from pathlib import Path


SPECIALTIES = [
    "cardiología",
    "endocrinología",
    "neurología",
    "oncología",
    "pediatría",
    "dermatología",
    "neumología",
    "gastroenterología",
    "medicina interna",
    "urgencias",
    "cirugía general",
    "radiología",
    "farmacología",
    "epidemiología",
    "cuidados intensivos",
]

DOC_TYPES = [
    "Guía clínica",
    "Protocolo",
    "Resumen de evidencia",
    "Nota de investigación",
    "Caso clínico",
    "Checklist",
]

CONDITIONS = [
    {
        "name": "hipertensión arterial",
        "symptoms": ["cefalea", "mareo", "visión borrosa", "palpitaciones"],
        "tests": ["tensión arterial", "ECG", "perfil lipídico", "función renal"],
        "treatments": ["cambios en estilo de vida", "IECA", "ARA-II", "diuréticos"],
    },
    {
        "name": "diabetes tipo 2",
        "symptoms": ["poliuria", "polidipsia", "fatiga", "visión borrosa"],
        "tests": ["HbA1c", "glucemia en ayunas", "perfil lipídico", "microalbuminuria"],
        "treatments": ["dieta", "ejercicio", "metformina", "iSGLT2"],
    },
    {
        "name": "asma",
        "symptoms": ["disnea", "sibilancias", "tos nocturna", "opresión torácica"],
        "tests": ["espirometría", "FEV1", "peak flow", "pruebas alérgicas"],
        "treatments": ["SABA", "corticoides inhalados", "LABA", "plan de acción"],
    },
    {
        "name": "EPOC",
        "symptoms": ["disnea crónica", "tos productiva", "exacerbaciones"],
        "tests": ["espirometría", "gasometría", "radiografía de tórax"],
        "treatments": ["bronco-dilatadores", "rehabilitación pulmonar", "vacunación"],
    },
    {
        "name": "infarto agudo de miocardio",
        "symptoms": ["dolor torácico", "diaforesis", "náuseas", "disnea"],
        "tests": ["ECG", "troponinas", "angiografía"],
        "treatments": ["antiagregación", "reperfusión", "betabloqueantes"],
    },
    {
        "name": "ictus isquémico",
        "symptoms": ["hemiparesia", "afasia", "desviación facial"],
        "tests": ["TC craneal", "RM", "angiografía"],
        "treatments": ["trombólisis", "antiagregación", "rehabilitación"],
    },
    {
        "name": "infección urinaria",
        "symptoms": ["disuria", "polaquiuria", "dolor suprapúbico"],
        "tests": ["urocultivo", "tira reactiva", "sedimento"],
        "treatments": ["antibióticos", "hidratación", "control de síntomas"],
    },
    {
        "name": "neumonía adquirida en la comunidad",
        "symptoms": ["fiebre", "tos", "expectoración", "dolor torácico"],
        "tests": ["radiografía de tórax", "PCR", "hemocultivos"],
        "treatments": ["antibióticos", "oxigenoterapia", "soporte"],
    },
    {
        "name": "insuficiencia cardíaca",
        "symptoms": ["disnea", "edemas", "ortopnea"],
        "tests": ["BNP", "ecocardiograma", "radiografía"],
        "treatments": ["diuréticos", "IECA", "betabloqueantes"],
    },
    {
        "name": "anemia ferropénica",
        "symptoms": ["fatiga", "palidez", "taquicardia"],
        "tests": ["hemograma", "ferritina", "hierro sérico"],
        "treatments": ["suplementos de hierro", "evaluar sangrado"],
    },
    {
        "name": "migraña",
        "symptoms": ["cefalea pulsátil", "fotofobia", "náuseas"],
        "tests": ["anamnesis", "descartar banderas rojas"],
        "treatments": ["AINEs", "triptanes", "profilaxis"],
    },
    {
        "name": "hipotiroidismo",
        "symptoms": ["fatiga", "aumento de peso", "frío"],
        "tests": ["TSH", "T4 libre"],
        "treatments": ["levotiroxina"],
    },
]

EVIDENCE_NOTES = [
    "La evidencia reciente sugiere optimizar el control de comorbilidades.",
    "Se recomienda individualizar objetivos terapéuticos según riesgo.",
    "El seguimiento estrecho reduce reingresos y complicaciones.",
    "El cribado oportuno mejora el pronóstico a largo plazo.",
]


def build_document(index: int, rng: random.Random, language: str) -> dict:
    condition = rng.choice(CONDITIONS)
    specialty = rng.choice(SPECIALTIES)
    doc_type = rng.choice(DOC_TYPES)

    title = f"{doc_type}: {condition['name'].capitalize()} en {specialty}"
    symptoms = ", ".join(condition["symptoms"])
    tests = ", ".join(condition["tests"])
    treatments = ", ".join(condition["treatments"])
    evidence = rng.choice(EVIDENCE_NOTES)
    guideline = rng.choice(["GPC 2023", "NICE 2022", "OMS 2021", "ESC 2024"])

    content = (
        f"Resumen clínico: Documento de referencia para {condition['name']} en el área de {specialty}.\n\n"
        f"Síntomas frecuentes: {symptoms}.\n"
        f"Factores de riesgo: edad, comorbilidades, hábitos de vida.\n"
        f"Pruebas recomendadas: {tests}.\n"
        f"Tratamiento inicial: {treatments}.\n"
        f"Seguimiento: control periódico y ajuste terapéutico según respuesta.\n"
        f"Notas de evidencia: {evidence}\n"
        f"Guía de referencia: {guideline}.\n"
        "Advertencia: material informativo para pruebas técnicas, no sustituye criterio clínico."
    )

    keywords = list(
        {
            condition["name"],
            specialty,
            "protocolo",
            "diagnóstico",
            "tratamiento",
        }
    )

    return {
        "id": f"med-{index:06d}",
        "title": title,
        "content": content,
        "keywords": keywords,
        "metadata": {
            "category": specialty,
            "language": language,
            "source": "synthetic://medical-dataset",
            "created_at": datetime.utcnow().isoformat(),
            "condition": condition["name"],
            "doc_type": doc_type,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic medical documents")
    parser.add_argument("--count", type=int, default=500, help="Number of documents")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--output",
        type=str,
        default="data/sample_documents.json",
        help="Output JSON path",
    )
    parser.add_argument("--language", type=str, default="es", help="Language code")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    documents = [build_document(i + 1, rng, args.language) for i in range(args.count)]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

    print(f"✅ Sample documents created: {output_path}")
    print(f"   Total documents: {len(documents)}")


if __name__ == "__main__":
    main()
