"""Gera a anotação assistida por IA dos 200 títulos adicionais.

O vocabulário e as regras refletem o guia do projeto. O resultado deve ser
tratado como anotação assistida por IA e submetido a controle de qualidade.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


INPUT = Path("data/annotations/audio_and_video_additional_200.jsonl")
OUTPUT = Path("data/annotations/audio_and_video_additional_200_reviewed.jsonl")


PRODUCT_PATTERNS = [
    r"\bCaixa Acústica Amplificada\b",
    r"\bProjetor Multimídia\b",
    r"\bApresentador de Slides\b",
    r"\bTela de Projeção\b",
    r"\bFones? de Ouvido\b",
    r"\bCaixa de Som\b",
    r"\bCaixa Som\b",
    r"\bCaixa Amplificada\b",
    r"\bCaixa Multiuso\b",
    r"\bSistema de Som\b",
    r"\bDVD Blu-Ray Player\b",
    r"\bSmart Speaker\b",
    r"\bSmart Screen\b",
    r"\bMini System\b",
    r"\bMicro System\b",
    r"\bPortable System\b",
    r"\bSom Portátil\b",
    r"\bToca-Discos\b",
    r"\bToca-Disco\b",
    r"\bToca Disco\b",
    r"\bGarrafa Térmica\b",
    r"\bRelogio Smart\b",
    r"\bSmart Tv Box\b",
    r"\bDvd Player\b",
    r"\biPod touch\b",
    r"\bAmplificador\b",
    r"\bHeadphones\b",
    r"\bHeadphone\b",
    r"\bHeadset\b",
    r"\bEarphone\b",
    r"\bEarhook\b",
    r"\bSoundbar\b",
    r"\bBoombox\b",
    r"\bVitrola\b",
    r"\bProjetor\b",
    r"\bPulseira\b",
    r"\bSuporte\b",
    r"\bTripé\b",
    r"\bSpeaker\b",
    r"\bSuper Bazooka\b",
    r"\bBazooka\b",
    r"\bMini Torre\b",
    r"\bSuper Torre\b",
    r"\bTorre\b",
    r"\bFone\b",
    r"\bRádio(?=\s+Retrô\b)",
]


BRAND_PATTERNS = [
    r"\bRibeiro e Pavani\b",
    r"\bHarman Kardon\b",
    r"\bMultilaser\b",
    r"\bGoldentec\b",
    r"\bMotorola\b",
    r"\bMicrosoft\b",
    r"\bPanasonic\b",
    r"\bLogitech\b",
    r"\bTrendwoo\b",
    r"\bMaxprint\b",
    r"\bSamsung\b",
    r"\bCorsair\b",
    r"\bPhilips\b",
    r"\bHuawei\b",
    r"\bAmazon\b",
    r"\bXiaomi\b",
    r"\bHyperX\b",
    r"\bHot Sat\b",
    r"\bAquário\b",
    r"\bPhilco\b",
    r"\bObabox\b",
    r"\bMultikids\b",
    r"\bFrahm\b",
    r"\bAmvox\b",
    r"\bExbom\b",
    r"\bUsams\b",
    r"\bSumay\b",
    r"\bEpson\b",
    r"\bApple\b",
    r"\bBeats\b",
    r"\bSony\b",
    r"\bNokia\b",
    r"\bTrust\b",
    r"\bAcer\b",
    r"\bIntel\b",
    r"\bNovik\b",
    r"\bJBL\b",
    r"\bLG\b",
    r"\bELG\b",
    r"\bNKS\b",
    r"\bTCL\b",
    r"\bBenq\b",
    r"\bGeonav\b",
    r"\bAwei\b",
    r"\bEdifier\b",
    r"\bUE\b",
    r"\bGT\b",
    r"\bR&P\b",
]


CONNECTIVITY_PATTERNS = [
    r"\bBluetooth(?:\s*\d(?:\.\d+)?)?\b",
    r"\bBluetooh(?:\s*\d(?:\.\d+)?)?\b",
    r"\bWi-?Fi(?:\s*\d+(?:\.\d+)?)?\b",
    r"\bType\s*C\b",
    r"\bHDMI(?:\s*ARC)?\b",
    r"\bHDM\b",
    r"\bÓptico\b",
    r"\bRj09\b",
    r"\bUSB(?:-[A-Z])?\b",
    r"\bTWS\b",
    r"\bRCA\b",
    r"\bAUX\b",
    r"\bVGA\b",
    r"\bP2\b",
    r"\bBT\b",
    r"\bSD\b",
    r"\bAV\b",
]


COLOR_PATTERNS = [
    r"\bRose Gold\b",
    r"\bChampagne Gold\b",
    r"\bAzul Marinho\b",
    r"\bVermelho\b",
    r"\bVermelha\b",
    r"\bCamuflado\b",
    r"\bCamuflada\b",
    r"\bPrateado\b",
    r"\bPrateada\b",
    r"\bChampagne\b",
    r"\bChampanhe\b",
    r"\bRaspberry\b",
    r"\bLaranja\b",
    r"\bAmarelo\b",
    r"\bAmarela\b",
    r"\bDourado\b",
    r"\bDourada\b",
    r"\bBranco\b",
    r"\bBranca\b",
    r"\bPreto\b",
    r"\bPreta\b",
    r"\bCinza\b",
    r"\bPrata\b",
    r"\bSilver\b",
    r"\bCarbon\b",
    r"\bVerde\b",
    r"\bAzul\b",
    r"\bRosa\b",
    r"\bRoxo\b",
    r"\bRoxa\b",
    r"\bBlack\b",
    r"\bWhite\b",
    r"\bBlue\b",
    r"\bRed\b",
    r"\bGold\b",
]


POWER_PATTERNS = [
    r"\b\d+(?:[.,]\d+)?\s*\+\s*\d+(?:[.,]\d+)?\s*W(?:\s*,?\s*RMS)?\b",
    r"\b(?:\d+\s*[xX]\s*)?\d+(?:[.,]\d+)?\s*W(?:\s*,?\s*RMS)?\b",
    r"\b\d+(?:[.,]\d+)?\s*Watts\b",
]


def add_entity(entities: list[list], start: int, end: int, label: str) -> None:
    if any(not (end <= old_start or start >= old_end) for old_start, old_end, _ in entities):
        return
    entities.append([start, end, label])


def add_patterns(text: str, entities: list[list], patterns: list[str], label: str) -> None:
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            add_entity(entities, match.start(), match.end(), label)


def annotate_products(text: str, entities: list[list]) -> None:
    add_patterns(text, entities, PRODUCT_PATTERNS, "PRODUTO")

    # Quando o título começa com "Caixa" sem um tipo mais específico,
    # Bluetooth permanece uma entidade separada de conectividade.
    if re.match(r"^Caixa\b", text, flags=re.IGNORECASE) and not any(
        label == "PRODUTO" and start == 0 for start, _, label in entities
    ):
        match = re.match(r"^Caixa\b", text, flags=re.IGNORECASE)
        add_entity(entities, match.start(), match.end(), "PRODUTO")

    # Remove tipos secundários usados como descrição/componente do produto.
    primary = [text[start:end].casefold() for start, end, label in entities if label == "PRODUTO"]
    filtered = []
    for entity in entities:
        start, end, label = entity
        value = text[start:end].casefold()
        if label != "PRODUTO":
            filtered.append(entity)
            continue
        if any(item.startswith("caixa") for item in primary) and value in {
            "speaker",
            "torre",
            "mini torre",
            "super torre",
            "mini system",
            "micro system",
        }:
            continue
        if "fone de ouvido" in primary and value in {
            "fone",
            "headphone",
            "headset",
            "earhook",
        }:
            continue
        if "suporte" in primary and value in {"headset", "projetor"} and start > text.casefold().find("suporte"):
            continue
        if "tripé" in primary and value == "caixa amplificada":
            continue
        if "pulseira" in primary and value == "ipod touch":
            continue
        if "tela de projeção" in primary and value == "tripé":
            continue
        if "smart screen" in primary and value == "projetor":
            continue
        if "mini system" in primary and value == "torre":
            continue
        filtered.append(entity)
    entities[:] = filtered


def annotate(text: str) -> dict:
    entities: list[list] = []
    annotate_products(text, entities)
    add_patterns(text, entities, BRAND_PATTERNS, "MARCA")

    # Pulse é marca somente quando aparece como palavra independente em linhas
    # em que não representa um modelo de Motorola/Sony/Multilaser.
    pulse_is_model = bool(
        re.search(r"\b(?:Motorola|Sony|JBL)\b", text, flags=re.IGNORECASE)
        or re.search(r"\bMultilaser\b.*\bPulse\b", text, flags=re.IGNORECASE)
    )
    if not pulse_is_model:
        add_patterns(text, entities, [r"\bPulse\b", r"\bPulsePRO\b"], "MARCA")

    # Em "Pulse Head Beats", Beats faz parte do nome do modelo.
    if re.search(r"\bPulse Head Beats\b", text, flags=re.IGNORECASE):
        entities[:] = [
            entity
            for entity in entities
            if not (entity[2] == "MARCA" and text[entity[0] : entity[1]].casefold() == "beats")
        ]

    add_patterns(text, entities, CONNECTIVITY_PATTERNS, "CONECTIVIDADE")
    add_patterns(text, entities, COLOR_PATTERNS, "COR")
    add_patterns(text, entities, POWER_PATTERNS, "POTENCIA")
    entities.sort(key=lambda entity: (entity[0], entity[1], entity[2]))
    return {"text": text, "entities": entities}


def validate(rows: list[dict]) -> None:
    if len(rows) != 200:
        raise ValueError(f"Esperados 200 registros; encontrados {len(rows)}")
    if len({row["text"] for row in rows}) != len(rows):
        raise ValueError("Existem títulos duplicados")
    for row_number, row in enumerate(rows, 1):
        text = row["text"]
        previous_end = -1
        for start, end, label in row["entities"]:
            if label not in {"PRODUTO", "MARCA", "CONECTIVIDADE", "COR", "POTENCIA"}:
                raise ValueError(f"TAG inválida no registro {row_number}: {label}")
            if not 0 <= start < end <= len(text):
                raise ValueError(f"Offset inválido no registro {row_number}")
            if start < previous_end:
                raise ValueError(f"Sobreposição no registro {row_number}")
            previous_end = end


def main() -> None:
    source = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reviewed = [annotate(row["text"]) for row in source]
    validate(reviewed)
    with OUTPUT.open("w", encoding="utf-8") as destination:
        for row in reviewed:
            destination.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Arquivo criado: {OUTPUT}")
    print(f"Registros: {len(reviewed)}")
    print(f"Entidades: {sum(len(row['entities']) for row in reviewed)}")


if __name__ == "__main__":
    main()
