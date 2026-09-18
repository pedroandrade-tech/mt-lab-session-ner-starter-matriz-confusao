"""Combina as bases revisadas e registra sua procedência."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


DOCCANO_REVIEWED = Path("data/annotations/audio_and_video_pilot_100_reviewed.jsonl")
AI_ASSISTED = Path("data/annotations/audio_and_video_additional_200_reviewed.jsonl")
OUTPUT = Path("data/annotations/audio_and_video_annotated_300.jsonl")
MANIFEST = Path("results/audio_and_video_annotated_300_manifest.json")
ALLOWED_LABELS = {"PRODUTO", "MARCA", "CONECTIVIDADE", "COR", "POTENCIA"}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if set(row) != {"text", "entities"}:
                raise ValueError(f"Campos inválidos em {path}, linha {line_number}")
            rows.append(row)
    return rows


def validate(rows: list[dict]) -> None:
    if len(rows) != 300:
        raise ValueError(f"Esperados 300 registros; encontrados {len(rows)}")
    texts = [row["text"] for row in rows]
    if len(set(texts)) != len(texts):
        raise ValueError("Há títulos duplicados na base combinada")

    for row_number, row in enumerate(rows, 1):
        text = row["text"]
        previous_end = -1
        for entity in row["entities"]:
            if not isinstance(entity, list) or len(entity) != 3:
                raise ValueError(f"Entidade inválida no registro {row_number}")
            start, end, label = entity
            if label not in ALLOWED_LABELS:
                raise ValueError(f"TAG inválida no registro {row_number}: {label}")
            if not 0 <= start < end <= len(text):
                raise ValueError(f"Offset inválido no registro {row_number}: {entity}")
            if start < previous_end:
                raise ValueError(f"Sobreposição no registro {row_number}")
            previous_end = end


def main() -> None:
    doccano_rows = load_jsonl(DOCCANO_REVIEWED)
    ai_rows = load_jsonl(AI_ASSISTED)
    rows = doccano_rows + ai_rows
    validate(rows)

    with OUTPUT.open("w", encoding="utf-8") as destination:
        for row in rows:
            destination.write(json.dumps(row, ensure_ascii=False) + "\n")

    counts = Counter(entity[2] for row in rows for entity in row["entities"])
    manifest = {
        "dataset": str(OUTPUT),
        "records": len(rows),
        "entities": sum(counts.values()),
        "labels": dict(sorted(counts.items())),
        "sources": [
            {
                "file": str(DOCCANO_REVIEWED),
                "records": len(doccano_rows),
                "annotation": "revisão humana no Doccano",
            },
            {
                "file": str(AI_ASSISTED),
                "records": len(ai_rows),
                "annotation": "anotação assistida por IA conforme o guia do projeto",
            },
        ],
        "validation": {
            "unique_texts": len({row["text"] for row in rows}),
            "invalid_offsets": 0,
            "overlaps": 0,
        },
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Base criada: {OUTPUT}")
    print(f"Registros: {len(rows)}")
    print(f"Entidades: {sum(counts.values())}")
    print(f"Distribuição: {dict(sorted(counts.items()))}")
    print(f"Manifesto: {MANIFEST}")


if __name__ == "__main__":
    main()
