#!/usr/bin/env python3
"""Compara pré-anotações com uma base-ouro revisada manualmente."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDICTIONS = REPO_ROOT / "data/annotations/audio_and_video_pilot_100.jsonl"
DEFAULT_GOLD = REPO_ROOT / "data/annotations/audio_and_video_pilot_100_reviewed.jsonl"
DEFAULT_REPORT = REPO_ROOT / "results/preannotation_evaluation.json"
DEFAULT_ERRORS = REPO_ROOT / "results/preannotation_errors.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Avalia entidades por correspondência exata de início, fim e TAG."
    )
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--errors", type=Path, default=DEFAULT_ERRORS)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record.get("text"), str):
                raise ValueError(f"{path}: linha {line_number} sem campo text válido")
            if not isinstance(record.get("entities"), list):
                raise ValueError(f"{path}: linha {line_number} sem campo entities válido")
            records.append(record)
    return records


def entity_set(record: dict) -> set[tuple[int, int, str]]:
    return {tuple(entity) for entity in record["entities"]}


def scores(counter: Counter) -> dict:
    tp, fp, fn = counter["tp"], counter["fp"], counter["fn"]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "predicted": tp + fp,
        "support_gold": tp + fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def main() -> None:
    args = parse_args()
    args.predictions = args.predictions.resolve()
    args.gold = args.gold.resolve()
    args.report = args.report.resolve()
    args.errors = args.errors.resolve()
    predictions = load_jsonl(args.predictions)
    gold = load_jsonl(args.gold)

    if len(predictions) != len(gold):
        raise ValueError("Os arquivos possuem quantidades diferentes de registros")

    labels = sorted(
        {
            entity[2]
            for record in predictions + gold
            for entity in record["entities"]
        }
    )
    by_label = {label: Counter() for label in labels}
    overall = Counter()
    error_rows = []
    exact_records = 0

    for index, (prediction, reference) in enumerate(zip(predictions, gold), 1):
        if prediction["text"] != reference["text"]:
            raise ValueError(f"Textos diferentes na linha {index}")

        text = reference["text"]
        predicted_entities = entity_set(prediction)
        gold_entities = entity_set(reference)
        true_positives = predicted_entities & gold_entities
        false_positives = predicted_entities - gold_entities
        false_negatives = gold_entities - predicted_entities

        if not false_positives and not false_negatives:
            exact_records += 1

        overall.update(
            tp=len(true_positives), fp=len(false_positives), fn=len(false_negatives)
        )

        for label in labels:
            predicted_label = {entity for entity in predicted_entities if entity[2] == label}
            gold_label = {entity for entity in gold_entities if entity[2] == label}
            by_label[label].update(
                tp=len(predicted_label & gold_label),
                fp=len(predicted_label - gold_label),
                fn=len(gold_label - predicted_label),
            )

        for error_type, entities in (("FP", false_positives), ("FN", false_negatives)):
            for start, end, label in sorted(entities):
                error_rows.append(
                    {
                        "record": index,
                        "error_type": error_type,
                        "label": label,
                        "start": start,
                        "end": end,
                        "entity_text": text[start:end],
                        "text": text,
                    }
                )

    label_metrics = {label: scores(by_label[label]) for label in labels}
    micro = scores(overall)
    macro_f1 = sum(metric["f1"] for metric in label_metrics.values()) / len(labels)
    report = {
        "method": "strict exact match: start, end and label",
        "predictions": str(args.predictions.relative_to(REPO_ROOT)),
        "gold": str(args.gold.relative_to(REPO_ROOT)),
        "records": len(gold),
        "exact_records": exact_records,
        "changed_records": len(gold) - exact_records,
        "micro": micro,
        "macro_f1": macro_f1,
        "per_label": label_metrics,
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    args.errors.parent.mkdir(parents=True, exist_ok=True)
    with args.errors.open("w", encoding="utf-8", newline="") as destination:
        fieldnames = [
            "record",
            "error_type",
            "label",
            "start",
            "end",
            "entity_text",
            "text",
        ]
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(error_rows)

    print("TAG             TP   FP   FN  Precisão   Recall       F1")
    for label, metric in label_metrics.items():
        print(
            f"{label:<15} {metric['tp']:>3}  {metric['fp']:>3}  {metric['fn']:>3}  "
            f"{metric['precision']:>8.3f}  {metric['recall']:>7.3f}  {metric['f1']:>7.3f}"
        )
    print(
        f"{'MICRO':<15} {micro['tp']:>3}  {micro['fp']:>3}  {micro['fn']:>3}  "
        f"{micro['precision']:>8.3f}  {micro['recall']:>7.3f}  {micro['f1']:>7.3f}"
    )
    print(f"F1 macro: {macro_f1:.3f}")
    print(f"Registros totalmente corretos: {exact_records}/{len(gold)}")
    print(f"Relatório: {args.report}")
    print(f"Erros: {args.errors}")


if __name__ == "__main__":
    main()
