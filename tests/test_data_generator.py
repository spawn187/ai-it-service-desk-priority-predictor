from __future__ import annotations

from it_ticket_priority.config import PRIORITY_ORDER
from it_ticket_priority.data_generator import (
    GenerationConfig,
    generate_synthetic_tickets,
    validate_generated_schema,
)
from it_ticket_priority.data_validation import clean_and_validate_data


def test_generator_is_reproducible() -> None:
    config = GenerationConfig(
        rows=500,
        seed=123,
        missing_rate=0.0,
        duplicate_rate=0.0,
    )
    first = generate_synthetic_tickets(config)
    second = generate_synthetic_tickets(config)
    assert first.equals(second)


def test_generated_schema_and_priority_distribution() -> None:
    frame = generate_synthetic_tickets(
        GenerationConfig(
            rows=2_000,
            seed=42,
            missing_rate=0.0,
            duplicate_rate=0.0,
        )
    )
    validate_generated_schema(frame)
    assert set(frame["priority"].unique()) == set(PRIORITY_ORDER)
    p1_ratio = (frame["priority"] == "P1").mean()
    assert 0.035 <= p1_ratio <= 0.05


def test_cleaning_removes_inserted_duplicates() -> None:
    frame = generate_synthetic_tickets(
        GenerationConfig(rows=1_000, seed=42, duplicate_rate=0.02)
    )
    cleaned, report = clean_and_validate_data(frame)
    assert report.duplicate_rows_removed > 0
    assert len(cleaned) < len(frame)
