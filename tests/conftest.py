from __future__ import annotations

import json
import joblib
import pytest
from sklearn.linear_model import LogisticRegression

from it_ticket_priority.config import FEATURE_COLUMNS, TARGET_COLUMN
from it_ticket_priority.data_generator import GenerationConfig, generate_synthetic_tickets
from it_ticket_priority.data_validation import clean_and_validate_data
from it_ticket_priority.inference import TicketPriorityPredictor
from it_ticket_priority.pipeline import build_pipeline


@pytest.fixture(scope="session")
def trained_predictor(tmp_path_factory: pytest.TempPathFactory) -> TicketPriorityPredictor:
    output_dir = tmp_path_factory.mktemp("model")
    model_path = output_dir / "model.joblib"
    metadata_path = output_dir / "metadata.json"

    frame = generate_synthetic_tickets(
        GenerationConfig(
            rows=1_200,
            seed=7,
            missing_rate=0.0,
            duplicate_rate=0.0,
        )
    )
    cleaned, _ = clean_and_validate_data(frame)
    pipeline = build_pipeline(
        LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=500,
            solver="lbfgs",
            random_state=7,
        ),
        max_text_features=700,
    )
    pipeline.fit(cleaned[FEATURE_COLUMNS], cleaned[TARGET_COLUMN])
    joblib.dump(pipeline, model_path)
    metadata_path.write_text(json.dumps({"model_version": "test"}), encoding="utf-8")
    return TicketPriorityPredictor(model_path=model_path, metadata_path=metadata_path)
