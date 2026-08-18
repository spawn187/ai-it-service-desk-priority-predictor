from __future__ import annotations

from sklearn.linear_model import LogisticRegression

from it_ticket_priority.config import FEATURE_COLUMNS, PRIORITY_ORDER, TARGET_COLUMN
from it_ticket_priority.data_generator import GenerationConfig, generate_synthetic_tickets
from it_ticket_priority.data_validation import clean_and_validate_data
from it_ticket_priority.pipeline import build_pipeline


def test_pipeline_trains_and_predicts_valid_priorities() -> None:
    frame = generate_synthetic_tickets(
        GenerationConfig(
            rows=800,
            seed=21,
            missing_rate=0.0,
            duplicate_rate=0.0,
        )
    )
    cleaned, _ = clean_and_validate_data(frame)
    model = build_pipeline(
        LogisticRegression(
            class_weight="balanced",
            max_iter=500,
            solver="lbfgs",
            random_state=21,
        ),
        max_text_features=500,
    )
    model.fit(cleaned[FEATURE_COLUMNS], cleaned[TARGET_COLUMN])
    predictions = model.predict(cleaned[FEATURE_COLUMNS].head(20))
    assert len(predictions) == 20
    assert set(predictions).issubset(set(PRIORITY_ORDER))
