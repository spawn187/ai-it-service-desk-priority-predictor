#!/usr/bin/env python
"""Run one local inference example."""

from __future__ import annotations

import json

from it_ticket_priority.inference import TicketPriorityPredictor

EXAMPLE_TICKET = {
    "description": (
        "Warehouse users cannot complete scanning transactions. All warehouse "
        "processing is blocked and there is no practical workaround."
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
    "related_incidents_30d": 6,
}


def main() -> None:
    result = TicketPriorityPredictor().predict(EXAMPLE_TICKET)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
