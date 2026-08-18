#!/usr/bin/env python
"""Evaluate an existing model against a generated or supplied dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from it_ticket_priority.config import DEFAULT_MODEL_PATH, FEATURE_COLUMNS, TARGET_COLUMN
from it_ticket_priority.data_generator import GenerationConfig, generate_synthetic_tickets
from it_ticket_priority.data_validation import clean_and_validate_data
from it_ticket_priority.evaluate import calculate_classification_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--data", type=Path, default=None)
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = (
        pd.read_csv(args.data)
        if args.data is not None
        else generate_synthetic_tickets(GenerationConfig(rows=args.rows, seed=args.seed))
    )
    cleaned, _ = clean_and_validate_data(frame)
    _, test = train_test_split(
        cleaned,
        test_size=0.20,
        random_state=args.seed,
        stratify=cleaned[TARGET_COLUMN],
    )
    pipeline = joblib.load(args.model)
    predictions = pipeline.predict(test[FEATURE_COLUMNS])
    metrics = calculate_classification_metrics(test[TARGET_COLUMN], predictions)
    print(pd.Series({key: value for key, value in metrics.items() if not isinstance(value, dict)}))


if __name__ == "__main__":
    main()
