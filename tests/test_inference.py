from __future__ import annotations

from it_ticket_priority.inference import TicketPriorityPredictor

EXAMPLE = {
    "description": (
        "The logistics application cannot process orders. All warehouse processing "
        "is blocked and multiple sites are affected."
    ),
    "category": "business_application",
    "channel": "phone",
    "service_criticality": "mission_critical",
    "site": "warehouse_north",
    "affected_users": 180,
    "vip_user": 0,
    "outage_indicator": 1,
    "security_indicator": 0,
    "business_hours": 1,
    "related_incidents_30d": 7,
}


def test_predictor_returns_probabilities_and_explanation(
    trained_predictor: TicketPriorityPredictor,
) -> None:
    result = trained_predictor.predict(EXAMPLE)
    assert result["predicted_priority"] in {"P1", "P2", "P3", "P4"}
    assert 0.0 <= result["confidence"] <= 1.0
    assert abs(sum(result["probabilities"].values()) - 1.0) < 1e-6
    assert isinstance(result["top_contributors"], list)
    assert result["model_version"] == "test"
