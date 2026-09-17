# -*- coding: utf-8 -*-

import json
import re
from pathlib import Path

INPUT_FILE = Path("data/processed/audio_and_video_clean.jsonl")
OUTPUT_FILE = Path("data/annotations/audio_and_video_preannotated.jsonl")

COLORS = [
    "preto", "preta", "branco", "branca", "azul", "vermelho", "vermelha",
    "verde", "cinza", "prata", "prateado", "prateada", "rosa", "roxo",
    "roxa", "amarelo", "amarela", "laranja", "dourado", "dourada",
    "camuflado", "camuflada"
]

CONNECTIVITY_PATTERNS = [
    r"\bBluetooth(?:\s*\d+(?:\.\d+)?)?\b",
    r"\bWi-?Fi(?:\s*\d+(?:\.\d+)?)?\b",
    r"\bUSB(?:-[A-Z])?\b",
    r"\bHDMI(?:\s*ARC)?\b",
    r"\bTWS\b",
    r"\bNFC\b",
    r"\bP2\b",
    r"\bRCA\b",
]

POWER_PATTERNS = [
    r"\b\d+(?:[.,]\d+)?\s*W(?:\s*RMS)?\b",
]

PRODUCT_TYPES = [
    "Caixa de Som",
    "Fone de Ouvido",
    "Fone",
    "Projetor Multimídia",
    "Projetor",
    "Soundbar",
    "Headset",
    "Microfone",
    "Home Theater",
]


def read_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Linha {n} ignorada: {e}")
    return rows


def add_entity(entities, start, end, label):
    if start < 0 or end <= start:
        return

    # Evita sobreposição exata/indevida
    for s, e, _ in entities:
        if not (end <= s or start >= e):
            return

    entities.append([start, end, label])


def find_exact(text, value, label, entities):
    if not value:
        return
    match = re.search(re.escape(value), text, flags=re.IGNORECASE)
    if match:
        add_entity(entities, match.start(), match.end(), label)


def annotate_record(record):
    text = record.get("name", "")
    entities = []

    # 1. PRODUTO / TIPO
    for product_type in PRODUCT_TYPES:
        match = re.search(re.escape(product_type), text, flags=re.IGNORECASE)
        if match:
            add_entity(entities, match.start(), match.end(), "PRODUTO")
            break

    # 2. MARCA
    brand = record.get("brand", "")
    find_exact(text, brand, "MARCA", entities)

    # 3. SKU, somente se aparecer literalmente no título
    sku = record.get("sku", "")
    find_exact(text, sku, "SKU", entities)

    # 4. COR
    for color in COLORS:
        for match in re.finditer(rf"\b{re.escape(color)}\b", text, flags=re.IGNORECASE):
            add_entity(entities, match.start(), match.end(), "COR")

    # 5. CONECTIVIDADE
    for pattern in CONNECTIVITY_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            add_entity(entities, match.start(), match.end(), "CONECTIVIDADE")

    # 6. POTÊNCIA
    for pattern in POWER_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            add_entity(entities, match.start(), match.end(), "POTENCIA")

    # Ordena entidades pelo início no texto
    entities.sort(key=lambda x: (x[0], x[1]))

    return {
        "text": text,
        "entities": entities,
    }


def main():
    if not INPUT_FILE.exists():
        print(f"ERRO: arquivo não encontrado: {INPUT_FILE}")
        return

    records = read_jsonl(INPUT_FILE)
    annotated = [annotate_record(r) for r in records if r.get("name")]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for row in annotated:
            json.dump(row, f, ensure_ascii=False)
            f.write("\n")

    print(f"Registros anotados: {len(annotated)}")
    print(f"Arquivo criado: {OUTPUT_FILE}")
    print("\nIMPORTANTE:")
    print("- Este arquivo contém PRÉ-ANOTAÇÕES automáticas.")
    print("- Revise manualmente no Doccano.")
    print("- MODELO não foi inferido automaticamente, pois é a entidade mais ambígua.")


if __name__ == "__main__":
    main()
