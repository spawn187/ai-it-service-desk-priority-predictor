"""Reusable model loading, prediction, and local explanation logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.pipeline import Pipeline

from .config import (
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    HUMAN_REVIEW_CONFIDENCE_THRESHOLD,
    MODEL_VERSION,
)
from .schemas import TicketRequest


class TicketPriorityPredictor:
    """Load a trained pipeline and expose a stable prediction interface."""

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL_PATH,
        metadata_path: str | Path = DEFAULT_METADATA_PATH,
    ) -> None:
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {self.model_path}. "
                "Run `python scripts/train_model.py`."
            )
        self.pipeline: Pipeline = joblib.load(self.model_path)
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, Any]:
        if not self.metadata_path.exists():
            return {"model_version": MODEL_VERSION}
        return json.loads(self.metadata_path.read_text(encoding="utf-8"))

    @property
    def model_version(self) -> str:
        return str(self.metadata.get("model_version", MODEL_VERSION))

    def predict(self, ticket: TicketRequest | dict[str, Any]) -> dict[str, Any]:
        """Predict priority and return confidence, probabilities, and explanation."""

        request = (
            ticket
            if isinstance(ticket, TicketRequest)
            else TicketRequest.model_validate(ticket)
        )
        frame = pd.DataFrame([request.model_dump()])
        predicted_priority = str(self.pipeline.predict(frame)[0])

        classifier = self.pipeline.named_steps["classifier"]
        if not hasattr(classifier, "predict_proba"):
            raise TypeError("The production estimator must implement predict_proba.")
        probability_values = self.pipeline.predict_proba(frame)[0]
        classes = [str(value) for value in classifier.classes_]
        probabilities = {
            label: float(probability)
            for label, probability in sorted(
                zip(classes, probability_values, strict=True),
                key=lambda item: item[0],
            )
        }
        confidence = float(max(probability_values))
        requires_review = (
            predicted_priority == "P1" or confidence < HUMAN_REVIEW_CONFIDENCE_THRESHOLD
        )

        return {
            "predicted_priority": predicted_priority,
            "confidence": confidence,
            "probabilities": probabilities,
            "requires_human_review": requires_review,
            "top_contributors": self._top_contributors(frame, predicted_priority),
            "model_version": self.model_version,
        }

    def _top_contributors(
        self,
        frame: pd.DataFrame,
        predicted_priority: str,
        limit: int = 5,
    ) -> list[dict[str, float | str]]:
        preprocessor = self.pipeline.named_steps["preprocessor"]
        classifier = self.pipeline.named_steps["classifier"]
        if not hasattr(classifier, "coef_"):
            return []

        transformed = preprocessor.transform(frame)
        feature_names = preprocessor.get_feature_names_out()
        class_index = list(classifier.classes_).index(predicted_priority)
        coefficients = classifier.coef_[class_index]

        if sparse.issparse(transformed):
            contributions = transformed.multiply(coefficients).toarray()[0]
        else:
            contributions = np.asarray(transformed)[0] * coefficients

        positive_indices = np.flatnonzero(contributions > 0)
        ranked = positive_indices[np.argsort(contributions[positive_indices])[::-1]][:limit]
        return [
            {
                "feature": self._clean_feature_name(str(feature_names[index])),
                "contribution": round(float(contributions[index]), 4),
            }
            for index in ranked
        ]

    @staticmethod
    def _clean_feature_name(name: str) -> str:
        replacements = {
            "text__": "text: ",
            "categorical__": "metadata: ",
            "numeric__": "numeric: ",
        }
        for prefix, replacement in replacements.items():
            if name.startswith(prefix):
                return name.replace(prefix, replacement, 1).replace("_", " ")
        return name.replace("_", " ")
