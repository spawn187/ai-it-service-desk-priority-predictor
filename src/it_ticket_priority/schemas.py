"""Shared API and inference schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TicketRequest(BaseModel):
    """Features required to score a service desk ticket."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    description: str = Field(min_length=3, max_length=4_000)
    category: str = Field(min_length=2, max_length=80)
    channel: str = Field(min_length=2, max_length=40)
    service_criticality: str = Field(min_length=2, max_length=40)
    site: str = Field(min_length=2, max_length=80)
    affected_users: int = Field(ge=0, le=100_000)
    vip_user: int = Field(ge=0, le=1)
    outage_indicator: int = Field(ge=0, le=1)
    security_indicator: int = Field(ge=0, le=1)
    business_hours: int = Field(ge=0, le=1)
    related_incidents_30d: int = Field(ge=0, le=10_000)

    @field_validator("category", "channel", "service_criticality", "site")
    @classmethod
    def normalize_enum_like_fields(cls, value: str) -> str:
        return value.lower().replace(" ", "_")


class FeatureContribution(BaseModel):
    feature: str
    contribution: float


class PredictionResponse(BaseModel):
    predicted_priority: str
    confidence: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float]
    requires_human_review: bool
    top_contributors: list[FeatureContribution]
    model_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
