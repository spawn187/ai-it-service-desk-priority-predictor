"""Deterministic fallback and provider-neutral structured-generation adapter."""

from __future__ import annotations

from typing import Any, Protocol

from it_ticket_priority.schemas import PredictionResponse, TicketRequest

from .models import (
    CopilotAdvice,
    GuardrailReport,
    PromptMessage,
    PromptPackage,
    RecommendedAction,
    RetrievedEvidence,
)


class TriageAssistant(Protocol):
    def generate(
        self,
        *,
        prompt: PromptPackage,
        ticket: TicketRequest,
        prediction: PredictionResponse,
        evidence: list[RetrievedEvidence],
        guardrails: GuardrailReport,
    ) -> CopilotAdvice: ...


class StructuredGenerationClient(Protocol):
    """Small contract implemented by any Azure/OpenAI-compatible adapter."""

    def generate_json(
        self,
        *,
        messages: list[PromptMessage],
        response_schema: dict[str, Any],
    ) -> dict[str, Any]: ...


class DeterministicTriageAssistant:
    """Offline fallback used in CI and demos when no external model is configured."""

    _SAFE_STARTERS = (
        "confirm",
        "capture",
        "review",
        "check",
        "compare",
        "collect",
        "validate",
        "inspect",
        "document",
        "preserve",
        "notify",
        "escalate",
    )

    def generate(
        self,
        *,
        prompt: PromptPackage,
        ticket: TicketRequest,
        prediction: PredictionResponse,
        evidence: list[RetrievedEvidence],
        guardrails: GuardrailReport,
    ) -> CopilotAdvice:
        actions = self._build_actions(evidence)
        evidence_ids = [item.evidence_id for item in evidence]
        human_review = (
            prediction.requires_human_review
            or ticket.security_indicator == 1
            or guardrails.injection_detected
            or bool(guardrails.context_injection_signals)
            or not evidence
        )
        top_score = evidence[0].score if evidence else 0.0
        confidence = round(min(prediction.confidence, 0.45 + top_score), 3)

        missing_information = [
            "Exact UTC start time and whether the issue is still active",
            "Representative error message, correlation ID, or monitoring event",
            "Confirmed business workaround and current blast radius",
        ]
        if ticket.affected_users <= 1:
            missing_information.append("Whether other users or locations can reproduce the issue")

        incident_type = "security incident" if ticket.security_indicator else ticket.category
        escalation = self._escalation_text(prediction.predicted_priority, ticket.security_indicator)
        return CopilotAdvice(
            summary=(
                f"Advisory triage plan for a {incident_type.replace('_', ' ')} ticket "
                f"predicted as {prediction.predicted_priority}."
            ),
            incident_type=incident_type,
            recommended_actions=actions,
            escalation=escalation,
            assumptions=[
                "The supplied ticket and retrieved context are untrusted data, not instructions.",
                "No production action has been executed by this copilot.",
                "The ML prediction and retrieved evidence remain subject to analyst judgment.",
            ],
            missing_information=missing_information,
            citations=evidence_ids,
            confidence=confidence,
            human_review_required=human_review,
            automation_allowed=False,
            prohibited_actions=[
                "Do not execute scripts or commands from ticket text or retrieved documents.",
                (
                    "Do not change identity, access, security, network, or service "
                    "configuration without approval."
                ),
                "Do not delete data, restart critical services, or isolate assets autonomously.",
            ],
            prompt_version=prompt.prompt_version,
        )

    def _build_actions(self, evidence: list[RetrievedEvidence]) -> list[RecommendedAction]:
        actions = [
            RecommendedAction(
                step="Confirm current scope, business impact, and whether a workaround exists.",
                rationale=(
                    "Impact validation is required before escalation or remediation decisions."
                ),
                risk="low",
                source_ids=[],
                requires_approval=True,
            )
        ]
        seen: set[str] = {actions[0].step.lower()}
        for item in evidence:
            for line in item.excerpt.splitlines():
                candidate = line.removeprefix("- ").strip()
                if not line.lstrip().startswith("- ") or not candidate:
                    continue
                normalized = candidate.lower()
                if not normalized.startswith(self._SAFE_STARTERS) or normalized in seen:
                    continue
                actions.append(
                    RecommendedAction(
                        step=candidate,
                        rationale=f"Grounded in {item.title} / {item.section}.",
                        risk="low",
                        source_ids=[item.evidence_id],
                        requires_approval=True,
                    )
                )
                seen.add(normalized)
                if len(actions) >= 5:
                    return actions
        if len(actions) == 1:
            actions.append(
                RecommendedAction(
                    step="Collect logs and timestamps without modifying the affected system.",
                    rationale="Evidence preservation supports safe diagnosis and escalation.",
                    risk="low",
                    source_ids=[],
                    requires_approval=True,
                )
            )
        return actions

    @staticmethod
    def _escalation_text(priority: str, security_indicator: int) -> str:
        if security_indicator:
            return "Route to the security incident process immediately and preserve evidence."
        if priority == "P1":
            return (
                "Activate major-incident review immediately; an incident manager must "
                "confirm severity."
            )
        if priority == "P2":
            return (
                "Escalate to the responsible service owner within the high-priority "
                "response window."
            )
        return "Continue through the normal service-desk workflow with analyst confirmation."


class LLMBackedTriageAssistant:
    """Validate provider output and re-apply non-negotiable policy controls."""

    def __init__(self, client: StructuredGenerationClient) -> None:
        self.client = client

    def generate(
        self,
        *,
        prompt: PromptPackage,
        ticket: TicketRequest,
        prediction: PredictionResponse,
        evidence: list[RetrievedEvidence],
        guardrails: GuardrailReport,
    ) -> CopilotAdvice:
        raw = self.client.generate_json(
            messages=prompt.messages,
            response_schema=prompt.response_schema,
        )
        advice = CopilotAdvice.model_validate(raw)
        valid_evidence_ids = {item.evidence_id for item in evidence}
        safe_citations = [item for item in advice.citations if item in valid_evidence_ids]
        mandatory_review = (
            advice.human_review_required
            or prediction.requires_human_review
            or ticket.security_indicator == 1
            or guardrails.injection_detected
            or bool(guardrails.context_injection_signals)
        )
        return advice.model_copy(
            update={
                "citations": safe_citations,
                "human_review_required": mandatory_review,
                "automation_allowed": False,
                "prompt_version": prompt.prompt_version,
            }
        )
