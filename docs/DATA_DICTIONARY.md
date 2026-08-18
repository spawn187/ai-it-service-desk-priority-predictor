# Data Dictionary

## Dataset contract

The full generated CSV contains one row per fictional ticket. The training pipeline uses only fields available or derivable at initial triage time.

| Column | Type | Allowed/example values | Purpose |
|---|---|---|---|
| `ticket_id` | string | `INC-1000000` | Synthetic identifier; excluded from modeling. |
| `description` | string | Free text | Primary NLP input. Missing text becomes an empty string. |
| `category` | categorical | `network`, `security`, `business_application`, etc. | High-level issue type. |
| `channel` | categorical | `portal`, `email`, `phone`, `monitoring` | Ticket source. |
| `service_criticality` | categorical | `low`, `medium`, `high`, `mission_critical` | Business criticality of the affected service. |
| `site` | categorical | `headquarters`, `warehouse_north`, etc. | Operational location. |
| `affected_users` | integer | 0-100,000 at API boundary | Estimated blast radius. |
| `vip_user` | binary integer | 0 or 1 | Whether a designated VIP is involved. |
| `outage_indicator` | binary integer | 0 or 1 | Whether a service outage is suspected. |
| `security_indicator` | binary integer | 0 or 1 | Whether a security signal is present. |
| `business_hours` | binary integer | 0 or 1 | Whether the ticket was raised during business hours. |
| `related_incidents_30d` | integer | 0 or greater | Recent related-incident count. |
| `priority` | categorical target | `P1`, `P2`, `P3`, `P4` | Synthetic target label. |

## Priority interpretation used by the generator

| Priority | Prototype interpretation |
|---|---|
| P1 | Critical, widespread, or immediately business-stopping incident. |
| P2 | High-impact incident affecting major functionality or multiple teams. |
| P3 | Moderate or limited-impact incident where operations can continue. |
| P4 | Low-impact incident or routine request. |

These definitions are illustrative. A real organization must map the model to its approved incident-priority matrix, including impact, urgency, service criticality, and regulatory requirements.

## Data generation behavior

The default generation run creates 30,000 base records and adds approximately 0.6% duplicate rows. It also introduces about 1.8% missingness into selected fields and noise into ticket text. Priorities are assigned from a latent severity score with fixed quantile boundaries, producing a deliberately imbalanced target.

The script is deterministic for a given configuration and seed:

```bash
python scripts/generate_data.py --rows 30000 --seed 42
```

## Excluded features and leakage risks

The following types of fields must not be used if they are produced after the priority decision:

- SLA breach or response-time outcome;
- final resolver group;
- analyst escalation note;
- closure or resolution code;
- incident duration;
- number of support actions after assignment;
- manual priority override;
- final business-impact assessment.

Including those values would create target leakage and inflate offline metrics without improving real-time triage.
