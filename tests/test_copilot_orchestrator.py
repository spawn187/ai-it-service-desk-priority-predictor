from it_ticket_priority.copilot.evaluation import EvaluationPredictor
from it_ticket_priority.copilot.orchestrator import ServiceDeskCopilot
from it_ticket_priority.schemas import TicketRequest


def test_major_outage_is_grounded_and_requires_human_review() -> None:
    ticket = TicketRequest(
        description="Warehouse WAN and DNS outage blocks all scanning and order processing.",
        category="network",
        channel="monitoring",
        service_criticality="mission_critical",
        site="warehouse_north",
        affected_users=220,
        vip_user=0,
        outage_indicator=1,
        security_indicator=0,
        business_hours=1,
        related_incidents_30d=6,
    )
    decision = ServiceDeskCopilot(EvaluationPredictor()).triage(ticket)
    assert decision.model_prediction.predicted_priority == "P1"
    assert any(item.document_id == "network_outage" for item in decision.evidence)
    assert decision.advice.citations
    assert decision.advice.human_review_required is True
    assert decision.advice.automation_allowed is False
    assert all(action.requires_approval for action in decision.advice.recommended_actions)
    assert any("P1" in item for item in decision.policy_decisions)
