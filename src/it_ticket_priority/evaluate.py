"""Model evaluation and visualization utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from .config import PRIORITY_ORDER


def calculate_classification_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, Any]:
    """Return portfolio-friendly aggregate and class-level metrics."""

    report = classification_report(
        y_true,
        y_pred,
        labels=PRIORITY_ORDER,
        output_dict=True,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "p1_precision": float(
            precision_score(y_true, y_pred, labels=["P1"], average="macro", zero_division=0)
        ),
        "p1_recall": float(
            recall_score(y_true, y_pred, labels=["P1"], average="macro", zero_division=0)
        ),
        "per_class": {
            label: {
                "precision": float(report[label]["precision"]),
                "recall": float(report[label]["recall"]),
                "f1_score": float(report[label]["f1-score"]),
                "support": int(report[label]["support"]),
            }
            for label in PRIORITY_ORDER
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=PRIORITY_ORDER).tolist(),
    }


def save_json(payload: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def plot_confusion_matrix(
    y_true: pd.Series,
    y_pred: np.ndarray,
    output_path: str | Path,
) -> None:
    """Save an annotated confusion matrix."""

    matrix = confusion_matrix(y_true, y_pred, labels=PRIORITY_ORDER)
    normalized = matrix / matrix.sum(axis=1, keepdims=True)
    annotations = np.empty_like(matrix, dtype=object)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            annotations[row, col] = f"{matrix[row, col]}\n{normalized[row, col]:.1%}"

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=annotations,
        fmt="",
        cmap="Blues",
        cbar=False,
        xticklabels=PRIORITY_ORDER,
        yticklabels=PRIORITY_ORDER,
    )
    plt.title("Priority prediction confusion matrix")
    plt.xlabel("Predicted priority")
    plt.ylabel("Actual priority")
    plt.tight_layout()
    plt.savefig(output, dpi=180, bbox_inches="tight")
    plt.close()


def plot_model_comparison(comparison: pd.DataFrame, output_path: str | Path) -> None:
    """Save a comparison chart for the candidate models."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    chart_data = comparison.set_index("model")[["accuracy", "macro_f1", "p1_recall"]]
    ax = chart_data.plot(kind="bar", figsize=(10, 6))
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Score")
    ax.set_xlabel("")
    ax.set_title("Candidate model comparison")
    ax.legend(loc="lower right")
    ax.tick_params(axis="x", rotation=0)
    plt.tight_layout()
    plt.savefig(output, dpi=180, bbox_inches="tight")
    plt.close()


def plot_class_distribution(labels: pd.Series, output_path: str | Path) -> None:
    """Save a class distribution chart."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    counts = labels.value_counts().reindex(PRIORITY_ORDER)
    ax = counts.plot(kind="bar", figsize=(8, 5))
    ax.set_title("Synthetic ticket priority distribution")
    ax.set_xlabel("Priority")
    ax.set_ylabel("Tickets")
    ax.tick_params(axis="x", rotation=0)
    for index, value in enumerate(counts):
        ax.text(index, value, f"{int(value):,}", ha="center", va="bottom")
    plt.tight_layout()
    plt.savefig(output, dpi=180, bbox_inches="tight")
    plt.close()
