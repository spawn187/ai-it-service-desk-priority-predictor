"""Lightweight experiment tracking with optional MLflow support."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _portable_artifact_name(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def log_experiment(
    run_name: str,
    params: dict[str, Any],
    metrics: dict[str, float],
    artifact_paths: list[Path] | None = None,
    fallback_path: Path | None = None,
) -> str:
    """Log to MLflow when configured, otherwise write a local JSON run record."""

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    if tracking_uri:
        try:
            import mlflow  # type: ignore[import-not-found]

            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "it-ticket-priority"))
            with mlflow.start_run(run_name=run_name):
                mlflow.log_params(params)
                mlflow.log_metrics(metrics)
                for artifact in artifact_paths or []:
                    if artifact.exists():
                        mlflow.log_artifact(str(artifact))
            return "mlflow"
        except ImportError:
            pass

    output = fallback_path or Path("artifacts/experiment_run.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "run_name": run_name,
                "params": params,
                "metrics": metrics,
                "artifacts": [_portable_artifact_name(path) for path in artifact_paths or []],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return "local_json"
