from fastapi.testclient import TestClient

import api.main as api_main
from it_ticket_priority.copilot.evaluation import EvaluationPredictor
from it_ticket_priority.copilot.orchestrator import ServiceDeskCopilot


PAYLOAD = {
    "description": "Warehouse WAN and DNS outage blocks all scanning and order processing.",
    "category": "network",
    "channel": "monitoring",
    "service_criticality": "mission_critical",
    "site": "warehouse_north",
    "affected_users": 220,
    "vip_user": 0,
    "outage_indicator": 1,
    "security_indicator": 0,
    "business_hours": 1,
    "related_incidents_30d": 6,
}


def test_copilot_endpoint_returns_grounded_controlled_decision(monkeypatch) -> None:
    copilot = ServiceDeskCopilot(EvaluationPredictor())
    monkeypatch.setattr(api_main, "get_copilot", lambda: copilot)
    client = TestClient(api_main.app)

    response = client.post("/copilot/triage", json=PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["model_prediction"]["predicted_priority"] == "P1"
    assert body["advice"]["human_review_required"] is True
    assert body["advice"]["automation_allowed"] is False
    assert body["advice"]["citations"]
    assert body["prompt_package"]["prompt_sha256"]
