from __future__ import annotations

from fastapi.testclient import TestClient

import api.main as api_main
from it_ticket_priority.inference import TicketPriorityPredictor


PAYLOAD = {
    "description": "A complete warehouse outage is blocking all scanning transactions.",
    "category": "business_application",
    "channel": "monitoring",
    "service_criticality": "mission_critical",
    "site": "warehouse_south",
    "affected_users": 220,
    "vip_user": 0,
    "outage_indicator": 1,
    "security_indicator": 0,
    "business_hours": 1,
    "related_incidents_30d": 9,
}


def test_prediction_endpoint(
    trained_predictor: TicketPriorityPredictor,
    monkeypatch,
) -> None:
    monkeypatch.setattr(api_main, "get_predictor", lambda: trained_predictor)
    client = TestClient(api_main.app)
    response = client.post("/predict", json=PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_priority"] in {"P1", "P2", "P3", "P4"}
    assert "probabilities" in body


def test_invalid_payload_is_rejected() -> None:
    client = TestClient(api_main.app)
    response = client.post("/predict", json={"description": "x"})
    assert response.status_code == 422
