#!/usr/bin/env python
"""Generate the reproducible synthetic ticket dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

from it_ticket_priority.config import DEFAULT_DATA_PATH, DEFAULT_SAMPLE_DATA_PATH
from it_ticket_priority.data_generator import GenerationConfig, save_synthetic_tickets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=30_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--sample-output", type=Path, default=DEFAULT_SAMPLE_DATA_PATH)
    parser.add_argument("--sample-rows", type=int, default=25)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = save_synthetic_tickets(
        args.output,
        GenerationConfig(rows=args.rows, seed=args.seed),
    )
    args.sample_output.parent.mkdir(parents=True, exist_ok=True)
    frame.head(args.sample_rows).to_csv(args.sample_output, index=False)
    print(f"Generated {len(frame):,} rows at {args.output}")
    print(f"Saved {args.sample_rows} sample rows at {args.sample_output}")


if __name__ == "__main__":
    main()
