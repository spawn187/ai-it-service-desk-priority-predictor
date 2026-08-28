"""Pydantic contracts for the prompt-engineering and RAG layer."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from it_ticket_priority.schemas import PredictionResponse


class RedactionEvent(BaseModel):
    """Summary of a sensitive-data pattern removed before prompting."""

    kind: str
    count: int = Field(ge=1)


class GuardrailReport(BaseModel):
    """Security decisions made before any generative model is called."""

    injection_detected: bool = False
    injection_signals: list[str] = Field(default_factory=list)
    context_injection_signals: list[str] = Field(default_factory=list)
    redactions: list[RedactionEvent] = Field(default_factory=list)
    input_truncated: bool = False
    automation_allowed: bool = False
    notes: list[str] = Field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return sum(event.count for event in self.redactions)


class RetrievedEvidence(BaseModel):
    """One grounded runbook fragment returned by the local retriever."""

    evidence_id: str
    document_id: str
    title: str
    section: str
    source_path: str
    score: float = Field(ge=0.0, le=1.0)
    excerpt: str


class PromptMessage(BaseModel):
    role: Literal["system", "developer", "user"]
    content: str


class PromptPackage(BaseModel):
    """Auditable, provider-neutral prompt artifact."""

    prompt_id: str
    prompt_version: str
    messages: list[PromptMessage]
    response_schema: dict[str, Any]
    evidence_ids: list[str]
    input_sha256: str
    prompt_sha256: str


class RecommendedAction(BaseModel):
    step: str
    rationale: str
    risk: Literal["low", "medium", "high"] = "low"
    source_ids: list[str] = Field(default_factory=list)
    requires_approval: bool = True


class CopilotAdvice(BaseModel):
    """Validated structured output expected from any assistant implementation."""

    model_config = ConfigDict(extra="forbid")

    summary: str
    incident_type: str
    recommended_actions: list[RecommendedAction]
    escalation: str
    assumptions: list[str]
    missing_information: list[str]
    citations: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    human_review_required: bool
    automation_allowed: bool = False
    prohibited_actions: list[str]
    prompt_version: str


class CopilotDecision(BaseModel):
    """End-to-end result shown through the API and Streamlit demo."""

    model_prediction: PredictionResponse
    guardrails: GuardrailReport
    evidence: list[RetrievedEvidence]
    advice: CopilotAdvice
    prompt_package: PromptPackage
    policy_decisions: list[str]


class PromptEvalCheck(BaseModel):
    name: str
    passed: bool
    detail: str


class PromptEvalResult(BaseModel):
    case_id: str
    passed: bool
    checks: list[PromptEvalCheck]


class PromptEvalSummary(BaseModel):
    suite_version: str
    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)
    failed_cases: int = Field(ge=0)
    pass_rate: float = Field(ge=0.0, le=1.0)
    results: list[PromptEvalResult]
    interpretation: str
