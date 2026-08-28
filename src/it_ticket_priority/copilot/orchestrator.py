"""Hybrid orchestration: ML prediction, guardrails, retrieval, and prompt contract."""

from __future__ import annotations

from typing import Any, Protocol

from it_ticket_priority.config import HUMAN_REVIEW_CONFIDENCE_THRESHOLD
from it_ticket_priority.schemas import PredictionResponse, TicketRequest

from .assistant import DeterministicTriageAssistant, TriageAssistant
from .models import CopilotDecision
from .prompting import PromptBuilder
from .retrieval import RunbookRetriever
from .security import sanitize_ticket_text, scan_context_for_injection


class PriorityPredictor(Protocol):
    def predict(self, ticket: TicketRequest | dict[str, Any]) -> dict[str, Any]: ...


class ServiceDeskCopilot:
    """Controlled decision-support workflow with no autonomous execution path."""

    def __init__(
        self,
        predictor: PriorityPredictor,
        *,
        retriever: RunbookRetriever | None = None,
        prompt_builder: PromptBuilder | None = None,
        assistant: TriageAssistant | None = None,
    ) -> None:
        self.predictor = predictor
        self.retriever = retriever or RunbookRetriever()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.assistant = assistant or DeterministicTriageAssistant()

    def triage(self, ticket: TicketRequest | dict[str, Any]) -> CopilotDecision:
        request = (
            ticket
            if isinstance(ticket, TicketRequest)
            else TicketRequest.model_validate(ticket)
        )
        safe_description, guardrails = sanitize_ticket_text(request.description)
        safe_ticket = request.model_copy(update={"description": safe_description})

        prediction = PredictionResponse.model_validate(self.predictor.predict(safe_ticket))
        query = " ".join(
            [
                safe_ticket.description,
                safe_ticket.category.replace("_", " "),
                safe_ticket.service_criticality.replace("_", " "),
                prediction.predicted_priority,
                "outage" if safe_ticket.outage_indicator else "",
                "security incident" if safe_ticket.security_indicator else "",
            ]
        )
        evidence = self.retriever.search(query, top_k=3)

        context_signals = scan_context_for_injection(
            (item.evidence_id, item.excerpt) for item in evidence
        )
        if context_signals:
            guardrails = guardrails.model_copy(
                update={
                    "injection_detected": True,
                    "context_injection_signals": context_signals,
                    "notes": [
                        *guardrails.notes,
                        (
                            "Indirect prompt-injection signal found in retrieved context; "
                            "review required."
                        ),
                    ],
                }
            )
            evidence = [
                item
                for item in evidence
                if not any(signal.startswith(f"{item.evidence_id}:") for signal in context_signals)
            ]

        prompt = self.prompt_builder.build(safe_ticket, prediction, evidence, guardrails)
        advice = self.assistant.generate(
            prompt=prompt,
            ticket=safe_ticket,
            prediction=prediction,
            evidence=evidence,
            guardrails=guardrails,
        )

        policy_decisions = self._policy_decisions(safe_ticket, prediction, guardrails, evidence)
        mandatory_review = (
            prediction.requires_human_review
            or safe_ticket.security_indicator == 1
            or guardrails.injection_detected
            or bool(guardrails.context_injection_signals)
            or not evidence
        )
        if mandatory_review:
            advice = advice.model_copy(
                update={
                    "human_review_required": True,
                    "automation_allowed": False,
                }
            )

        return CopilotDecision(
            model_prediction=prediction,
            guardrails=guardrails,
            evidence=evidence,
            advice=advice,
            prompt_package=prompt,
            policy_decisions=policy_decisions,
        )

    @staticmethod
    def _policy_decisions(
        ticket: TicketRequest,
        prediction: PredictionResponse,
        guardrails,
        evidence,
    ) -> list[str]:
        decisions: list[str] = []
        if prediction.predicted_priority == "P1":
            decisions.append("P1 predictions require major-incident analyst confirmation.")
        if prediction.confidence < HUMAN_REVIEW_CONFIDENCE_THRESHOLD:
            decisions.append("Prediction confidence is below the 65% review threshold.")
        if ticket.security_indicator:
            decisions.append("Security-related tickets must follow the security incident process.")
        if guardrails.injection_detected:
            decisions.append("Prompt-injection signal detected; no automated action is permitted.")
        if not evidence:
            decisions.append("No sufficiently relevant runbook evidence was retrieved.")
        decisions.append("Portfolio policy: all generated recommendations are advisory only.")
        return decisions
