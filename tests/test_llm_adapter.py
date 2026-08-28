from typing import Any

from it_ticket_priority.copilot.assistant import LLMBackedTriageAssistant
from it_ticket_priority.copilot.evaluation import EvaluationPredictor
from it_ticket_priority.copilot.models import PromptMessage
from it_ticket_priority.copilot.orchestrator import ServiceDeskCopilot
from it_ticket_priority.schemas import TicketRequest


class FakeClient:
    def generate_json(
        self,
        *,
        messages: list[PromptMessage],
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        del messages, response_schema
        return {
            "summary": "Validated provider output.",
            "incident_type": "security incident",
            "recommended_actions": [
                {
                    "step": "Preserve the alert and relevant logs.",
                    "rationale": "Evidence preservation.",
                    "risk": "low",
                    "source_ids": ["security_incident#safe-diagnostic-steps"],
                    "requires_approval": True,
                }
            ],
            "escalation": "Escalate to security.",
            "assumptions": ["No action was executed."],
            "missing_information": ["Exact UTC start time"],
            "citations": [
                "security_incident#safe-diagnostic-steps",
                "invented#citation",
            ],
            "confidence": 0.8,
            "human_review_required": False,
            "automation_allowed": True,
            "prohibited_actions": ["No autonomous isolation."],
            "prompt_version": "wrong-version",
        }


def test_provider_output_is_validated_and_policy_is_reapplied() -> None:
    ticket = TicketRequest(
        description="Defender detected a suspicious sign-in and possible credential compromise.",
        category="security",
        channel="monitoring",
        service_criticality="high",
        site="headquarters",
        affected_users=2,
        vip_user=0,
        outage_indicator=0,
        security_indicator=1,
        business_hours=1,
        related_incidents_30d=1,
    )
    assistant = LLMBackedTriageAssistant(FakeClient())
    decision = ServiceDeskCopilot(EvaluationPredictor(), assistant=assistant).triage(ticket)
    assert decision.advice.human_review_required is True
    assert decision.advice.automation_allowed is False
    assert decision.advice.prompt_version == decision.prompt_package.prompt_version
    assert "invented#citation" not in decision.advice.citations
