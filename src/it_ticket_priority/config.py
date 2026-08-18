"""Project-wide configuration and feature definitions."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
ARTIFACT_DIR = PROJECT_ROOT / "artifacts"
ASSET_DIR = PROJECT_ROOT / "assets"

def _configured_path(environment_variable: str, default: Path) -> Path:
    configured = os.getenv(environment_variable)
    if not configured:
        return default
    candidate = Path(configured).expanduser()
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


DEFAULT_MODEL_PATH = _configured_path("MODEL_PATH", MODEL_DIR / "priority_model.joblib")
DEFAULT_METADATA_PATH = _configured_path(
    "METADATA_PATH", MODEL_DIR / "model_metadata.json"
)
DEFAULT_DATA_PATH = DATA_DIR / "synthetic_tickets.csv"
DEFAULT_SAMPLE_DATA_PATH = DATA_DIR / "sample" / "sample_tickets.csv"

RANDOM_SEED = 42
TARGET_COLUMN = "priority"
TEXT_COLUMN = "description"

CATEGORICAL_COLUMNS = [
    "category",
    "channel",
    "service_criticality",
    "site",
]

NUMERIC_COLUMNS = [
    "affected_users",
    "vip_user",
    "outage_indicator",
    "security_indicator",
    "business_hours",
    "related_incidents_30d",
]

FEATURE_COLUMNS = [TEXT_COLUMN, *CATEGORICAL_COLUMNS, *NUMERIC_COLUMNS]
PRIORITY_ORDER = ["P1", "P2", "P3", "P4"]

MODEL_VERSION = "1.0.0"
HUMAN_REVIEW_CONFIDENCE_THRESHOLD = 0.65

# Class weights approximately balance the fixed synthetic distribution while
# adding a modest extra penalty for missed P1 incidents.
PRODUCTION_CLASS_WEIGHTS = {
    "P1": 7.8,
    "P2": 1.75,
    "P3": 0.62,
    "P4": 0.61,
}
