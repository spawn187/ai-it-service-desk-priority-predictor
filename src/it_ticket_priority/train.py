"""Training orchestration for the ticket priority classifier."""

from __future__ import annotations

import json
import platform
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import make_scorer, recall_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from .config import (
    ARTIFACT_DIR,
    ASSET_DIR,
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    FEATURE_COLUMNS,
    MODEL_VERSION,
    PRODUCTION_CLASS_WEIGHTS,
    PROJECT_ROOT,
    RANDOM_SEED,
    TARGET_COLUMN,
)
from .data_generator import GenerationConfig, generate_synthetic_tickets
from .data_validation import clean_and_validate_data
from .evaluate import (
    calculate_classification_metrics,
    plot_class_distribution,
    plot_confusion_matrix,
    plot_model_comparison,
    save_json,
)
from .pipeline import build_pipeline, candidate_estimators
from .tracking import log_experiment


@dataclass(frozen=True)
class TrainingConfig:
    rows: int = 30_000
    seed: int = RANDOM_SEED
    test_size: float = 0.20
    max_text_features: int = 12_000
    tune_logistic_regression: bool = True
    model_path: Path = DEFAULT_MODEL_PATH
    metadata_path: Path = DEFAULT_METADATA_PATH
    artifact_dir: Path = ARTIFACT_DIR
    asset_dir: Path = ASSET_DIR


def _portable_path(path: Path) -> str:
    """Return a repository-relative path when possible."""

    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def _select_business_best_index(cv_results: dict[str, Any]) -> int:
    """Select the CV candidate with the strongest P1-recall/macro-F1 trade-off."""

    macro_f1 = np.asarray(cv_results["mean_test_macro_f1"], dtype=float)
    p1_recall = np.asarray(cv_results["mean_test_p1_recall"], dtype=float)
    business_score = 0.55 * p1_recall + 0.45 * macro_f1
    return int(np.nanargmax(business_score))


def _p1_recall(y_true: pd.Series, y_pred: np.ndarray) -> float:
    return float(
        recall_score(y_true, y_pred, labels=["P1"], average="macro", zero_division=0)
    )


def _fit_logistic_pipeline(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    config: TrainingConfig,
) -> tuple[Pipeline, dict[str, Any]]:
    """Tune the regularization strength for the selected production model."""

    base_estimator = LogisticRegression(
        class_weight=PRODUCTION_CLASS_WEIGHTS,
        max_iter=1_000,
        solver="lbfgs",
        random_state=config.seed,
    )
    pipeline = build_pipeline(base_estimator, max_text_features=config.max_text_features)

    if not config.tune_logistic_regression:
        pipeline.set_params(classifier__C=4.0)
        pipeline.fit(x_train, y_train)
        return pipeline, {"classifier__C": 4.0, "cv_macro_f1": None, "cv_p1_recall": None}

    scorers = {
        "macro_f1": "f1_macro",
        "p1_recall": make_scorer(_p1_recall),
    }
    cross_validation = StratifiedKFold(n_splits=3, shuffle=True, random_state=config.seed)
    grid = GridSearchCV(
        estimator=pipeline,
        param_grid={"classifier__C": [0.5, 1.0, 2.0, 4.0]},
        scoring=scorers,
        refit=_select_business_best_index,
        cv=cross_validation,
        n_jobs=-1,
        verbose=0,
        return_train_score=False,
    )
    grid.fit(x_train, y_train)
    best_index = int(grid.best_index_)
    tuning_summary = {
        "classifier__C": float(grid.best_params_["classifier__C"]),
        "cv_macro_f1": float(grid.cv_results_["mean_test_macro_f1"][best_index]),
        "cv_p1_recall": float(grid.cv_results_["mean_test_p1_recall"][best_index]),
    }
    return grid.best_estimator_, tuning_summary


def _fit_candidate(
    name: str,
    estimator: BaseEstimator,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    config: TrainingConfig,
) -> tuple[Pipeline, float, dict[str, Any]]:
    start = time.perf_counter()
    if name == "logistic_regression":
        pipeline, details = _fit_logistic_pipeline(x_train, y_train, config)
    else:
        pipeline = build_pipeline(estimator, max_text_features=config.max_text_features)
        pipeline.fit(x_train, y_train)
        details = {}
    fit_seconds = time.perf_counter() - start
    return pipeline, fit_seconds, details


def train_project(
    frame: pd.DataFrame | None = None,
    config: TrainingConfig | None = None,
) -> dict[str, Any]:
    """Train candidate models, select logistic regression, and persist artifacts."""

    config = config or TrainingConfig()
    config.model_path.parent.mkdir(parents=True, exist_ok=True)
    config.metadata_path.parent.mkdir(parents=True, exist_ok=True)
    config.artifact_dir.mkdir(parents=True, exist_ok=True)
    config.asset_dir.mkdir(parents=True, exist_ok=True)

    if frame is None:
        frame = generate_synthetic_tickets(
            GenerationConfig(rows=config.rows, seed=config.seed)
        )

    cleaned, quality_report = clean_and_validate_data(frame)
    x = cleaned[FEATURE_COLUMNS]
    y = cleaned[TARGET_COLUMN]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=config.test_size,
        random_state=config.seed,
        stratify=y,
    )

    fitted_models: dict[str, Pipeline] = {}
    comparison_rows: list[dict[str, Any]] = []
    tuning_details: dict[str, Any] = {}

    for name, estimator in candidate_estimators().items():
        pipeline, fit_seconds, details = _fit_candidate(
            name,
            estimator,
            x_train,
            y_train,
            config,
        )
        predictions = pipeline.predict(x_test)
        metrics = calculate_classification_metrics(y_test, predictions)
        fitted_models[name] = pipeline
        comparison_rows.append(
            {
                "model": name,
                "accuracy": metrics["accuracy"],
                "macro_f1": metrics["macro_f1"],
                "weighted_f1": metrics["weighted_f1"],
                "p1_precision": metrics["p1_precision"],
                "p1_recall": metrics["p1_recall"],
                "fit_seconds": round(fit_seconds, 3),
            }
        )
        if details:
            tuning_details[name] = details

    comparison = pd.DataFrame(comparison_rows).sort_values(
        by=["p1_recall", "macro_f1", "accuracy"],
        ascending=False,
    )

    # Logistic regression is deliberately selected for production because it
    # provides calibrated-like probabilities, inspectable coefficients, and a
    # strong P1-recall/complexity trade-off. The comparison remains transparent.
    selected_model_name = "logistic_regression"
    selected_pipeline = fitted_models[selected_model_name]
    selected_predictions = selected_pipeline.predict(x_test)
    selected_metrics = calculate_classification_metrics(y_test, selected_predictions)

    joblib.dump(selected_pipeline, config.model_path, compress=3)

    comparison_path = config.artifact_dir / "model_comparison.csv"
    comparison.to_csv(comparison_path, index=False)

    metrics_path = config.artifact_dir / "metrics.json"
    quality_path = config.artifact_dir / "data_quality_report.json"
    prediction_sample_path = config.artifact_dir / "test_predictions_sample.csv"
    confusion_path = config.asset_dir / "confusion_matrix.png"
    comparison_figure_path = config.asset_dir / "model_comparison.png"
    distribution_path = config.asset_dir / "class_distribution.png"

    save_json(selected_metrics, metrics_path)
    save_json(quality_report.to_dict(), quality_path)

    sample_predictions = x_test.head(50).copy()
    sample_predictions["actual_priority"] = y_test.head(50).to_numpy()
    sample_predictions["predicted_priority"] = selected_predictions[:50]
    sample_predictions.to_csv(prediction_sample_path, index=False)

    plot_confusion_matrix(y_test, selected_predictions, confusion_path)
    plot_model_comparison(comparison, comparison_figure_path)
    plot_class_distribution(y, distribution_path)

    selected_row = comparison.loc[comparison["model"] == selected_model_name].iloc[0]
    metadata: dict[str, Any] = {
        "model_name": selected_model_name,
        "model_version": MODEL_VERSION,
        "trained_at_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "selection_rationale": (
            "Selected for high P1 recall, probability output, explainability, "
            "low inference cost, and operational simplicity."
        ),
        "training_config": {
            **asdict(config),
            "model_path": _portable_path(config.model_path),
            "metadata_path": _portable_path(config.metadata_path),
            "artifact_dir": _portable_path(config.artifact_dir),
            "asset_dir": _portable_path(config.asset_dir),
        },
        "data": {
            "input_rows": int(len(frame)),
            "clean_rows": int(len(cleaned)),
            "training_rows": int(len(x_train)),
            "test_rows": int(len(x_test)),
            "priority_distribution": y.value_counts(normalize=True).sort_index().to_dict(),
            "quality_report": quality_report.to_dict(),
        },
        "metrics": selected_metrics,
        "model_comparison": comparison.to_dict(orient="records"),
        "tuning": tuning_details,
        "runtime": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "selected_model_summary": selected_row.to_dict(),
        "feature_columns": FEATURE_COLUMNS,
    }
    config.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    tracking_backend = log_experiment(
        run_name=f"ticket-priority-{MODEL_VERSION}",
        params={
            "rows": len(cleaned),
            "test_size": config.test_size,
            "max_text_features": config.max_text_features,
            "selected_model": selected_model_name,
            "logistic_c": tuning_details.get(selected_model_name, {}).get("classifier__C", 4.0),
        },
        metrics={
            "accuracy": selected_metrics["accuracy"],
            "macro_f1": selected_metrics["macro_f1"],
            "weighted_f1": selected_metrics["weighted_f1"],
            "p1_precision": selected_metrics["p1_precision"],
            "p1_recall": selected_metrics["p1_recall"],
        },
        artifact_paths=[metrics_path, comparison_path, confusion_path],
        fallback_path=config.artifact_dir / "experiment_run.json",
    )

    return {
        "selected_model": selected_model_name,
        "metrics": selected_metrics,
        "comparison": comparison,
        "metadata": metadata,
        "tracking_backend": tracking_backend,
        "model_path": config.model_path,
    }
