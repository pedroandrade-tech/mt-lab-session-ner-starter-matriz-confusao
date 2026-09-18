"""Cria uma amostra-piloto reprodutível para revisão no Doccano."""

import json
import random
from collections import Counter
from pathlib import Path


INPUT = Path("data/annotations/audio_and_video_preannotated.jsonl")
OUTPUT = Path("data/annotations/audio_and_video_pilot_100.jsonl")
SEED = 42
ALLOWED_LABELS = {"PRODUTO", "MARCA", "CONECTIVIDADE", "COR", "POTENCIA"}


def load_unique_rows(path: Path) -> list[dict]:
    unique = {}
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, 1):
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
                raise ValueError(f"Texto vazio na linha {line_number}")
            unique.setdefault(text, {"text": text, "entities": entities})
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

    pilot = (
        rng.sample(without_entities, 20)
        + rng.sample(without_product, 30)
        + rng.sample(with_product, 50)
    )
    rng.shuffle(pilot)
    return pilot


def validate(rows: list[dict]) -> None:
    for row_number, row in enumerate(rows, 1):
        text = row["text"]
        previous_end = -1
        for start, end, label in sorted(row["entities"]):
            if not (0 <= start < end <= len(text)):
                raise ValueError(f"Offset inválido no registro {row_number}: {[start, end, label]}")
            if start < previous_end:
                raise ValueError(f"Sobreposição no registro {row_number}")
            previous_end = end


def main() -> None:
    rows = load_unique_rows(INPUT)
    pilot = sample_rows(rows)
    validate(pilot)

    with OUTPUT.open("w", encoding="utf-8") as file:
        for row in pilot:
            json.dump(row, file, ensure_ascii=False)
            file.write("\n")

    labels = Counter(entity[2] for row in pilot for entity in row["entities"])
    print(f"Amostra criada: {OUTPUT}")
    print(f"Títulos: {len(pilot)}")
    print(f"Distribuição de entidades: {dict(sorted(labels.items()))}")


if __name__ == "__main__":
    main()
