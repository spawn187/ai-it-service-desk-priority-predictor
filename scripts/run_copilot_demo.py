"""Run the full copilot workflow offline with an inspectable sample ticket."""

from __future__ import annotations

import json

from it_ticket_priority.copilot.evaluation import EvaluationPredictor
from it_ticket_priority.copilot.orchestrator import ServiceDeskCopilot
from it_ticket_priority.schemas import TicketRequest


def main() -> None:
    ticket = TicketRequest(
        description=(
            "Warehouse north has lost WAN and DNS connectivity. "
            "All scanning and order processing is blocked."
        ),
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
    # ASCII escaping keeps the CLI JSON portable across Windows legacy code pages.
    print(json.dumps(decision.model_dump(), indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
