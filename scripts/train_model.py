#!/usr/bin/env python
"""Train, compare, evaluate, and persist the portfolio model."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from it_ticket_priority.config import (
    ARTIFACT_DIR,
    ASSET_DIR,
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
)
from it_ticket_priority.data_generator import GenerationConfig, generate_synthetic_tickets
from it_ticket_priority.train import TrainingConfig, train_project


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=30_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data", type=Path, default=None, help="Optional existing CSV dataset")
    parser.add_argument("--quick", action="store_true", help="Fast smoke-test mode for CI")
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--metadata-path", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--asset-dir", type=Path, default=ASSET_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = min(args.rows, 3_000) if args.quick else args.rows
    frame = (
        pd.read_csv(args.data)
        if args.data is not None
        else generate_synthetic_tickets(GenerationConfig(rows=rows, seed=args.seed))
    )
    config = TrainingConfig(
        rows=rows,
        seed=args.seed,
        max_text_features=3_000 if args.quick else 12_000,
        tune_logistic_regression=not args.quick,
        model_path=args.model_path,
        metadata_path=args.metadata_path,
        artifact_dir=args.artifact_dir,
        asset_dir=args.asset_dir,
    )
    result = train_project(frame=frame, config=config)
    metrics = result["metrics"]
    print(f"Selected model: {result['selected_model']}")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Macro F1: {metrics['macro_f1']:.3f}")
    print(f"P1 recall: {metrics['p1_recall']:.3f}")
    print(f"Model saved to: {result['model_path']}")


if __name__ == "__main__":
    main()
