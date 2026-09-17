# -*- coding: utf-8 -*-

import json
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================

# Arquivo gerado pelo pré-processamento anterior
INPUT_FILE = Path("data/processed/audio_and_video_clean.jsonl")

# Arquivo pronto para importação no Doccano
OUTPUT_DIR = Path("data/annotations")
OUTPUT_FILE = OUTPUT_DIR / "audio_and_video_doccano.jsonl"


def read_jsonl(path):
    """
    Lê um arquivo JSONL e retorna uma lista de registros.
    """
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                print(
                    f"Aviso: linha {line_number} ignorada "
                    f"por JSON inválido: {error}"
                )

    return records


def prepare_for_doccano(records):
    """
    Converte os dados pré-processados para o formato JSONL
    adequado para importação e anotação no Doccano.

    O exercício pede NER a partir do título do produto,
    portanto usamos somente o campo 'name' como 'text'.

    Saída:
    {"text": "Caixa de Som JBL Boombox 3 Bluetooth Preta"}
    """
    output = []
    seen = set()

    for record in records:
        name = record.get("name", "")

        if not isinstance(name, str):
            continue

        # Remove apenas espaços externos.
        # Não altera o texto internamente para preservar os offsets do NER.
        text = name.strip()

        if not text:
            continue

        # Evita títulos duplicados
        if text in seen:
            continue

        seen.add(text)

        output.append({
            "text": text
        })

    return output


def save_jsonl(records, path):
    """
    Salva um registro JSON por linha.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for record in records:
            json.dump(record, file, ensure_ascii=False)
            file.write("\n")


def main():
    if not INPUT_FILE.exists():
        print(f"ERRO: arquivo não encontrado: {INPUT_FILE}")
        print(
            "Primeiro rode o script de pré-processamento "
            "prepare_audio_and_video.py."
        )
        return

    print(f"Lendo dados pré-processados: {INPUT_FILE}")

    records = read_jsonl(INPUT_FILE)

    print(f"Registros lidos: {len(records)}")

    doccano_records = prepare_for_doccano(records)

    print(
        f"Títulos preparados para anotação: "
        f"{len(doccano_records)}"
    )

    save_jsonl(doccano_records, OUTPUT_FILE)

    print("\nArquivo pronto para importar no Doccano:")
    print(OUTPUT_FILE)

    if doccano_records:
        print("\nExemplo:")
        print(
            json.dumps(
                doccano_records[0],
                ensure_ascii=False
            )
        )


if __name__ == "__main__":
    main()
