"""Dataset validation and cleaning utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from .config import FEATURE_COLUMNS, PRIORITY_ORDER, TARGET_COLUMN


@dataclass(frozen=True)
class DataQualityReport:
    input_rows: int
    output_rows: int
    duplicate_rows_removed: int
    rows_with_missing_description: int
    invalid_target_rows_removed: int
    missing_values_by_column: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def clean_and_validate_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, DataQualityReport]:
    """Validate required columns and return a clean modeling dataset."""

    required = {*FEATURE_COLUMNS, TARGET_COLUMN}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    input_rows = len(frame)
    missing_values = {column: int(frame[column].isna().sum()) for column in required}
    rows_with_missing_description = int(frame["description"].isna().sum())

    cleaned = frame.copy()
    if "ticket_id" in cleaned.columns:
        cleaned = cleaned.drop_duplicates(subset=["ticket_id", *FEATURE_COLUMNS, TARGET_COLUMN])
    else:
        cleaned = cleaned.drop_duplicates(subset=[*FEATURE_COLUMNS, TARGET_COLUMN])
    duplicates_removed = input_rows - len(cleaned)

    valid_target_mask = cleaned[TARGET_COLUMN].isin(PRIORITY_ORDER)
    invalid_target_rows = int((~valid_target_mask).sum())
    cleaned = cleaned.loc[valid_target_mask].copy()

    # Empty text is safer than dropping rows; TF-IDF can still combine it with metadata.
    cleaned["description"] = cleaned["description"].fillna("").astype(str)
    for column in ["category", "channel", "service_criticality", "site"]:
        cleaned[column] = cleaned[column].fillna("unknown").astype(str)

    report = DataQualityReport(
        input_rows=input_rows,
        output_rows=len(cleaned),
        duplicate_rows_removed=duplicates_removed,
        rows_with_missing_description=rows_with_missing_description,
        invalid_target_rows_removed=invalid_target_rows,
        missing_values_by_column=missing_values,
    )
    return cleaned.reset_index(drop=True), report
