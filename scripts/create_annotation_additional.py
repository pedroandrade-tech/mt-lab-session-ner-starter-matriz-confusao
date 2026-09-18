"""Cria uma amostra adicional, sem sobreposição com o piloto, para o Doccano."""

import json
import random
from collections import Counter
from pathlib import Path


INPUT = Path("data/annotations/audio_and_video_preannotated.jsonl")
PILOT = Path("data/annotations/audio_and_video_pilot_100.jsonl")
OUTPUT = Path("data/annotations/audio_and_video_additional_200.jsonl")
SEED = 43
ALLOWED_LABELS = {"PRODUTO", "MARCA", "CONECTIVIDADE", "COR", "POTENCIA"}


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("text", "")
            entities = [
                entity
                for entity in row.get("entities", [])
                if len(entity) == 3 and entity[2] in ALLOWED_LABELS
            ]
            if not text:
                raise ValueError(f"Texto vazio na linha {line_number} de {path}")
            rows.append({"text": text, "entities": entities})
    return rows


def unique_by_text(rows: list[dict]) -> list[dict]:
    unique = {}
    for row in rows:
        unique.setdefault(row["text"], row)
    return list(unique.values())


def sample_rows(rows: list[dict]) -> list[dict]:
    rng = random.Random(SEED)
    without_entities = [row for row in rows if not row["entities"]]
    without_product = [
        row
        for row in rows
        if row["entities"] and not any(entity[2] == "PRODUTO" for entity in row["entities"])
    ]
    with_product = [
        row
        for row in rows
        if any(entity[2] == "PRODUTO" for entity in row["entities"])
    ]

    # Superamostra casos difíceis, respeitando os 21 registros sem entidades
    # que restaram depois da criação do piloto.
    sample = (
        rng.sample(without_entities, 20)
        + rng.sample(without_product, 60)
        + rng.sample(with_product, 120)
    )
    rng.shuffle(sample)
    return sample


def validate(rows: list[dict], excluded_texts: set[str]) -> None:
    if len(rows) != 200:
        raise ValueError(f"A amostra deveria ter 200 registros, mas possui {len(rows)}")
    if len({row["text"] for row in rows}) != len(rows):
        raise ValueError("A amostra contém títulos duplicados")
    overlap = {row["text"] for row in rows} & excluded_texts
    if overlap:
        raise ValueError(f"Há {len(overlap)} títulos repetidos do piloto")

    for row_number, row in enumerate(rows, 1):
        text = row["text"]
        previous_end = -1
        for start, end, label in sorted(row["entities"]):
            if not (0 <= start < end <= len(text)):
                raise ValueError(
                    f"Offset inválido no registro {row_number}: {[start, end, label]}"
                )
            if start < previous_end:
                raise ValueError(f"Sobreposição no registro {row_number}")
            previous_end = end


def main() -> None:
    all_rows = unique_by_text(load_rows(INPUT))
    pilot_texts = {row["text"] for row in load_rows(PILOT)}
    candidates = [row for row in all_rows if row["text"] not in pilot_texts]
    additional = sample_rows(candidates)
    validate(additional, pilot_texts)

    with OUTPUT.open("w", encoding="utf-8") as destination:
        for row in additional:
            json.dump(row, destination, ensure_ascii=False)
            destination.write("\n")

    labels = Counter(entity[2] for row in additional for entity in row["entities"])
    print(f"Amostra criada: {OUTPUT}")
    print(f"Semente: {SEED}")
    print(f"Títulos: {len(additional)}")
    print(f"Sobreposição com o piloto: 0")
    print(f"Distribuição das pré-anotações: {dict(sorted(labels.items()))}")


if __name__ == "__main__":
    main()
