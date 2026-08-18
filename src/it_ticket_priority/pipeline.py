"""Feature engineering and model pipeline construction."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC

from .config import (
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    PRODUCTION_CLASS_WEIGHTS,
    RANDOM_SEED,
    TEXT_COLUMN,
)


def build_preprocessor(max_text_features: int = 12_000) -> ColumnTransformer:
    """Create the preprocessing graph for text, categorical, and numeric features."""

    text_transformer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        min_df=3,
        max_features=max_text_features,
        sublinear_tf=True,
        dtype=np.float64,
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("text", text_transformer, TEXT_COLUMN),
            ("categorical", categorical_transformer, CATEGORICAL_COLUMNS),
            ("numeric", numeric_transformer, NUMERIC_COLUMNS),
        ],
        remainder="drop",
        sparse_threshold=0.3,
        verbose_feature_names_out=True,
    )


def build_pipeline(estimator: BaseEstimator, max_text_features: int = 12_000) -> Pipeline:
    """Combine preprocessing and an estimator in a leakage-safe pipeline."""

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(max_text_features=max_text_features)),
            ("classifier", estimator),
        ]
    )


def candidate_estimators() -> Mapping[str, BaseEstimator]:
    """Return deterministic candidate estimators for benchmark comparison."""

    return {
        "logistic_regression": LogisticRegression(
            C=4.0,
            class_weight=PRODUCTION_CLASS_WEIGHTS,
            max_iter=1_000,
            solver="lbfgs",
            random_state=RANDOM_SEED,
        ),
        "linear_svm": LinearSVC(
            C=1.0,
            class_weight="balanced",
            random_state=RANDOM_SEED,
        ),
        "sgd_log_loss": SGDClassifier(
            loss="log_loss",
            alpha=1e-5,
            class_weight="balanced",
            max_iter=2_000,
            tol=1e-4,
            random_state=RANDOM_SEED,
        ),
    }
