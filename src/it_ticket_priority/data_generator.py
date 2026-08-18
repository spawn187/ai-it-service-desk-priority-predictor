"""Generate a reproducible synthetic IT service desk dataset.

The generator intentionally introduces ambiguity, missing values, spelling noise,
and imperfect relationships between incident text and labels. The result is useful
for demonstrating an end-to-end ML workflow without exposing real company data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS, PRIORITY_ORDER, RANDOM_SEED, TARGET_COLUMN


@dataclass(frozen=True)
class GenerationConfig:
    """Configuration for synthetic ticket generation."""

    rows: int = 30_000
    seed: int = RANDOM_SEED
    missing_rate: float = 0.018
    duplicate_rate: float = 0.006
    text_noise_rate: float = 0.12
    impact_phrase_mismatch_rate: float = 0.23
    severity_noise_sigma: float = 1.42


CATEGORIES: Final[tuple[str, ...]] = (
    "network",
    "identity_access",
    "endpoint",
    "collaboration",
    "business_application",
    "security",
    "hardware",
    "service_request",
)

CATEGORY_PROBABILITIES: Final[tuple[float, ...]] = (
    0.16,
    0.15,
    0.16,
    0.11,
    0.15,
    0.07,
    0.09,
    0.11,
)

CHANNELS: Final[tuple[str, ...]] = ("portal", "email", "phone", "monitoring")
CHANNEL_PROBABILITIES: Final[tuple[float, ...]] = (0.46, 0.26, 0.18, 0.10)

CRITICALITIES: Final[tuple[str, ...]] = ("low", "medium", "high", "mission_critical")
CRITICALITY_PROBABILITIES: Final[tuple[float, ...]] = (0.18, 0.42, 0.28, 0.12)
CRITICALITY_SCORES: Final[dict[str, float]] = {
    "low": 0.0,
    "medium": 0.9,
    "high": 1.8,
    "mission_critical": 3.1,
}

SITES: Final[tuple[str, ...]] = (
    "headquarters",
    "warehouse_north",
    "warehouse_south",
    "regional_office",
    "remote_user",
)
SITE_PROBABILITIES: Final[tuple[float, ...]] = (0.28, 0.22, 0.19, 0.16, 0.15)

CATEGORY_SCORES: Final[dict[str, float]] = {
    "network": 0.8,
    "identity_access": 0.4,
    "endpoint": 0.2,
    "collaboration": 0.3,
    "business_application": 0.7,
    "security": 1.4,
    "hardware": 0.1,
    "service_request": -1.2,
}

ISSUE_TEMPLATES: Final[dict[str, tuple[str, ...]]] = {
    "network": (
        "network connection is unavailable",
        "users cannot reach internal services",
        "high packet loss is affecting the site",
        "wireless access is unstable",
        "the WAN link keeps disconnecting",
    ),
    "identity_access": (
        "user cannot sign in to the corporate account",
        "multi-factor authentication is looping",
        "account is locked after repeated login attempts",
        "access to the shared resource is denied",
        "password reset did not restore access",
    ),
    "endpoint": (
        "Windows device is freezing during normal use",
        "managed laptop fails to install the required update",
        "endpoint protection reports an unhealthy state",
        "application crashes immediately after launch",
        "device performance has degraded significantly",
    ),
    "collaboration": (
        "Teams calls are dropping and audio is distorted",
        "mail delivery is delayed",
        "shared mailbox cannot be opened",
        "calendar invitations are not synchronizing",
        "video meetings cannot be joined",
    ),
    "business_application": (
        "the logistics application cannot process orders",
        "warehouse users cannot complete scanning transactions",
        "the finance system returns an unexpected error",
        "the customer portal is responding slowly",
        "the ERP workflow is stuck before approval",
    ),
    "security": (
        "endpoint protection detected suspicious activity",
        "a potentially malicious email was opened",
        "multiple failed sign-ins were detected",
        "unauthorized access may have occurred",
        "ransomware-like file changes were observed",
    ),
    "hardware": (
        "the docking station is not detected",
        "the laptop battery no longer charges",
        "a warehouse scanner is not powering on",
        "the monitor displays no signal",
        "the printer repeatedly jams",
    ),
    "service_request": (
        "software installation is requested",
        "a new shared mailbox is required",
        "access to an application is requested",
        "a standard laptop setup is needed",
        "a distribution list membership change is requested",
    ),
}

IMPACT_PHRASES: Final[dict[str, tuple[str, ...]]] = {
    "P1": (
        "business operations are stopped for all users",
        "there is a complete service outage across multiple sites",
        "all warehouse processing is blocked",
        "the incident has widespread and immediate business impact",
    ),
    "P2": (
        "multiple teams are affected and a critical function is unavailable",
        "service is severely degraded for many users",
        "a major business process is blocked with no practical workaround",
        "the issue has high operational impact",
    ),
    "P3": (
        "the impact is limited and a workaround is available",
        "one team is experiencing an intermittent issue",
        "the service is degraded but core operations continue",
        "several users are affected without a complete outage",
    ),
    "P4": (
        "the request affects a single user and has low urgency",
        "this is a routine request with no service interruption",
        "the issue is cosmetic and business operations continue",
        "assistance is needed when capacity allows",
    ),
}

CONTEXT_PHRASES: Final[tuple[str, ...]] = (
    "The issue started after a recent change.",
    "No reliable workaround has been confirmed.",
    "The user already restarted the device.",
    "The problem has occurred more than once today.",
    "Monitoring generated a related alert.",
    "The requester included a screenshot and error code.",
    "The service desk reproduced the issue once.",
    "The exact start time is not known.",
)

TYPO_REPLACEMENTS: Final[dict[str, str]] = {
    "service": "servce",
    "users": "usres",
    "network": "netwrok",
    "application": "applicaton",
    "access": "acess",
    "warehouse": "warehosue",
    "connection": "conection",
    "request": "requst",
}


def _assign_priority(score: np.ndarray) -> np.ndarray:
    """Assign priorities using fixed quantiles to preserve realistic imbalance."""

    p1_cut = np.quantile(score, 0.958)
    p2_cut = np.quantile(score, 0.815)
    p3_cut = np.quantile(score, 0.410)
    return np.select(
        [score >= p1_cut, score >= p2_cut, score >= p3_cut],
        ["P1", "P2", "P3"],
        default="P4",
    )


def _nearby_priority(priority: str, rng: np.random.Generator) -> str:
    idx = PRIORITY_ORDER.index(priority)
    candidates = [idx]
    if idx > 0:
        candidates.append(idx - 1)
    if idx < len(PRIORITY_ORDER) - 1:
        candidates.append(idx + 1)
    return PRIORITY_ORDER[int(rng.choice(candidates))]


def _apply_text_noise(text: str, rng: np.random.Generator) -> str:
    words = text.split()
    if not words:
        return text
    replacement_candidates = [
        index
        for index, word in enumerate(words)
        if word.lower().strip(".,") in TYPO_REPLACEMENTS
    ]
    if replacement_candidates:
        idx = int(rng.choice(replacement_candidates))
        clean = words[idx].lower().strip(".,")
        suffix = "." if words[idx].endswith(".") else "," if words[idx].endswith(",") else ""
        words[idx] = TYPO_REPLACEMENTS[clean] + suffix
    elif len(words) > 5:
        idx = int(rng.integers(1, len(words) - 1))
        words.pop(idx)
    return " ".join(words)


def _build_descriptions(
    categories: np.ndarray,
    priorities: np.ndarray,
    sites: np.ndarray,
    channels: np.ndarray,
    config: GenerationConfig,
    rng: np.random.Generator,
) -> list[str]:
    descriptions: list[str] = []
    for category, priority, site, channel in zip(
        categories, priorities, sites, channels, strict=True
    ):
        issue = str(rng.choice(ISSUE_TEMPLATES[str(category)]))
        phrase_priority = str(priority)
        if rng.random() < config.impact_phrase_mismatch_rate:
            phrase_priority = _nearby_priority(str(priority), rng)
        impact = str(rng.choice(IMPACT_PHRASES[phrase_priority]))
        context = str(rng.choice(CONTEXT_PHRASES))
        description = (
            f"{issue.capitalize()} at {str(site).replace('_', ' ')}. "
            f"{impact.capitalize()}. Reported through {channel}. {context}"
        )
        if rng.random() < config.text_noise_rate:
            description = _apply_text_noise(description, rng)
        descriptions.append(description)
    return descriptions


def generate_synthetic_tickets(config: GenerationConfig | None = None) -> pd.DataFrame:
    """Return a reproducible synthetic ticket dataset."""

    config = config or GenerationConfig()
    if config.rows < 100:
        raise ValueError("rows must be at least 100")

    rng = np.random.default_rng(config.seed)
    n = config.rows

    categories = rng.choice(CATEGORIES, size=n, p=CATEGORY_PROBABILITIES)
    channels = rng.choice(CHANNELS, size=n, p=CHANNEL_PROBABILITIES)
    criticalities = rng.choice(CRITICALITIES, size=n, p=CRITICALITY_PROBABILITIES)
    sites = rng.choice(SITES, size=n, p=SITE_PROBABILITIES)

    outage_probability = np.where(
        np.isin(categories, ["network", "business_application", "collaboration"]),
        0.23,
        0.055,
    )
    outage = rng.binomial(1, outage_probability)

    security_probability = np.where(categories == "security", 0.76, 0.025)
    security = rng.binomial(1, security_probability)

    vip = rng.binomial(1, 0.07, size=n)
    business_hours = rng.binomial(1, 0.73, size=n)

    base_users = rng.lognormal(mean=1.45, sigma=1.05, size=n)
    impact_multiplier = (
        1
        + outage * rng.uniform(2.0, 7.0, size=n)
        + (criticalities == "mission_critical") * rng.uniform(0.8, 2.8, size=n)
    )
    affected_users = np.clip(np.rint(base_users * impact_multiplier), 1, 2_500).astype(int)
    single_user_mask = (
        np.isin(categories, ["hardware", "service_request", "identity_access"])
        & (outage == 0)
    )
    affected_users[single_user_mask & (rng.random(n) < 0.62)] = 1

    related_incidents = rng.poisson(
        0.8
        + 2.8 * outage
        + 1.4 * security
        + 0.7 * (channels == "monitoring"),
        size=n,
    )
    related_incidents = np.clip(related_incidents, 0, 35)

    criticality_score = np.array([CRITICALITY_SCORES[str(value)] for value in criticalities])
    category_score = np.array([CATEGORY_SCORES[str(value)] for value in categories])

    severity_score = (
        criticality_score
        + category_score
        + 2.25 * outage
        + 2.20 * security
        + 0.32 * np.log1p(affected_users)
        + 0.55 * vip
        + 0.17 * related_incidents
        + 0.35 * (channels == "monitoring")
        + 0.18 * (business_hours == 0)
        + rng.normal(0.0, config.severity_noise_sigma, size=n)
    )

    priorities = _assign_priority(severity_score)
    descriptions = _build_descriptions(categories, priorities, sites, channels, config, rng)

    frame = pd.DataFrame(
        {
            "ticket_id": [f"INC-{1_000_000 + i}" for i in range(n)],
            "description": descriptions,
            "category": categories,
            "channel": channels,
            "service_criticality": criticalities,
            "site": sites,
            "affected_users": affected_users,
            "vip_user": vip,
            "outage_indicator": outage,
            "security_indicator": security,
            "business_hours": business_hours,
            "related_incidents_30d": related_incidents,
            TARGET_COLUMN: priorities,
        }
    )

    # Add a small amount of missingness to realistic input fields.
    nullable_columns = [
        "description",
        "category",
        "channel",
        "service_criticality",
        "site",
        "affected_users",
        "related_incidents_30d",
    ]
    for column in nullable_columns:
        mask = rng.random(n) < config.missing_rate
        frame.loc[mask, column] = np.nan

    # Insert exact duplicate records; validation code is expected to remove them.
    duplicate_count = int(n * config.duplicate_rate)
    if duplicate_count:
        duplicate_rows = frame.sample(duplicate_count, random_state=config.seed).copy()
        frame = pd.concat([frame, duplicate_rows], ignore_index=True)
        frame = frame.sample(frac=1.0, random_state=config.seed).reset_index(drop=True)

    return frame


def save_synthetic_tickets(
    output_path: str | Path,
    config: GenerationConfig | None = None,
) -> pd.DataFrame:
    """Generate and save the synthetic dataset as CSV."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_synthetic_tickets(config)
    frame.to_csv(output, index=False)
    return frame


def validate_generated_schema(frame: pd.DataFrame) -> None:
    """Raise a descriptive error when generated data does not match the contract."""

    required = {"ticket_id", *FEATURE_COLUMNS, TARGET_COLUMN}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Generated dataset is missing required columns: {sorted(missing)}")
    invalid_priorities = set(frame[TARGET_COLUMN].dropna().unique()).difference(PRIORITY_ORDER)
    if invalid_priorities:
        raise ValueError(
            "Generated dataset contains invalid priorities: "
            f"{sorted(invalid_priorities)}"
        )
