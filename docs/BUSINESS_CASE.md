# Business Case and Rollout Model

## Positioning

This project is not based on the claim that AI should replace service-desk analysts. The value hypothesis is that a controlled assistant can improve the consistency, speed, and traceability of triage while keeping people responsible for the decision.

The business case must be validated with organizational data. The examples below are explicitly illustrative and are not presented as realized savings.

## Problems the solution targets

- inconsistent P1-P4 prioritization;
- time spent gathering scope, impact, time, workaround, and evidence;
- delayed use of approved runbooks;
- avoidable reassignment and escalation;
- undocumented assumptions;
- low visibility into why an analyst accepted or changed a decision;
- ungoverned experimentation with generative AI;
- fragmented ownership between business, ITSM, security, and engineering.

## Value levers

### 1. Triage-time reduction

The copilot can pre-assemble:

- predicted priority and confidence;
- relevant runbook evidence;
- safe first-response steps;
- missing-information questions;
- escalation recommendation;
- policy and review status.

The analyst still validates and edits the result.

### 2. Consistency

A common decision policy can reduce variation across shifts and teams. Consistency should be measured through disagreement, override reasons, and escalation outcomes—not assumed from standardized wording.

### 3. Major-incident risk reduction

The ML layer is selected with strong P1 recall as an explicit objective. A real organization must quantify the cost of a missed P1 versus false escalation and approve thresholds accordingly.

### 4. Knowledge adoption

Evidence IDs make runbook use visible. Monitoring can reveal which domains lack relevant knowledge, where runbooks are stale, and which recommendations analysts repeatedly reject.

### 5. Auditability and governance

The system records prompt version, hashes, model version, evidence IDs, guardrail decisions, and human-review status. This creates a better control surface than unmanaged copy-and-paste use of a public chatbot.

### 6. Foundation for constrained automation

The portfolio keeps automation disabled. Once decision quality, identity, authorization, change control, and rollback are proven, selected low-risk steps could be assessed separately. The initial business case does not depend on autonomous remediation.

## Benefit calculation framework

Define:

- `V` = tickets processed per month;
- `T0` = current average first-triage effort in minutes;
- `T1` = assisted average first-triage effort in minutes;
- `A` = analyst adoption rate;
- `Q` = proportion of assisted outputs accepted or useful after review;
- `C` = fully loaded analyst cost per hour;
- `R` = monthly operating cost of the AI service;
- `I` = monthly implementation/amortized change cost during rollout.

Estimated monthly productive capacity released:

```text
Hours released = V × (T0 - T1) × A × Q / 60
```

Estimated gross capacity value:

```text
Gross capacity value = Hours released × C
```

Estimated net monthly value:

```text
Net value = Gross capacity value - R - I
```

This is capacity value, not automatically cash saving. It becomes financial value only if the organization can redeploy the time, avoid hiring, improve SLA outcomes, or reduce incident cost.

## Illustrative scenarios

### Scenario A: small service operation

Assumptions:

- 500 tickets/month;
- 2 minutes average useful time reduction;
- 60% adoption;
- 75% useful-output rate.

```text
500 × 2 × 0.60 × 0.75 / 60 = 7.5 hours/month
```

This may not justify complex infrastructure. A lightweight local or shared service could still be valuable for consistency and learning.

### Scenario B: medium service operation

Assumptions:

- 5,000 tickets/month;
- 3 minutes time reduction;
- 70% adoption;
- 80% useful-output rate.

```text
5,000 × 3 × 0.70 × 0.80 / 60 = 140 hours/month
```

The organization would then compare 140 hours of productive capacity, quality benefits, and risk reduction with platform, provider, support, evaluation, and change costs.

### Scenario C: major-incident benefit

A separate model should estimate:

```text
Expected avoided loss = reduction in missed/delayed critical escalations
                      × average impact per event
```

This value is highly organization-specific and should be calculated with incident data, not guessed in a portfolio.

## Costs to include

- data extraction, anonymization, and label review;
- runbook cleanup and ownership;
- engineering and integration;
- model/provider inference;
- hosting, storage, network, and observability;
- security, privacy, risk, legal, and architecture review;
- analyst training and change management;
- evaluation and ongoing quality review;
- incident response and on-call support;
- prompt, model, and corpus maintenance;
- decommissioning or fallback costs.

## Risk-adjusted value

Benefits should be discounted for:

- outputs requiring substantial edits;
- low adoption;
- incorrect priority or escalation;
- weak knowledge coverage;
- provider downtime;
- cost volatility;
- policy or privacy constraints;
- additional analyst checking time;
- potential harm from automation bias.

The objective is not the largest theoretical ROI. It is a credible value case that survives operational and risk review.

## Rollout stages and gates

### Stage 0: problem validation

Deliverables:

- current-process map;
- baseline time and quality metrics;
- risk classification;
- data inventory;
- stakeholder and owner map;
- decision on whether AI is appropriate.

Exit gate:

- measurable problem and accountable sponsor;
- approved scope and no simpler solution overlooked.

### Stage 1: offline prototype

Deliverables:

- anonymized benchmark;
- ML and provider comparison;
- runbook corpus;
- threat model;
- acceptance thresholds;
- cost model.

Exit gate:

- zero hard safety failures;
- quality above approved threshold;
- architecture/security/privacy approval to proceed.

### Stage 2: shadow mode

The system scores real tickets but does not affect workflow.

Measure:

- prediction agreement;
- P1 misses and false escalations;
- retrieval relevance;
- schema success;
- latency and cost;
- segment performance;
- failure patterns.

Exit gate:

- stable quality and operational behavior;
- accepted thresholds and documented residual risks.

### Stage 3: analyst assist

Analysts see suggestions and must explicitly accept or edit them.

Measure:

- adoption;
- acceptance and edit rate;
- time to first useful response;
- override reasons;
- analyst trust and satisfaction;
- major-incident escalation outcomes;
- safety events.

Exit gate:

- sustained benefit without unacceptable error or workload shift.

### Stage 4: constrained integration

Only separately approved, low-risk workflow changes may be introduced. Examples might include adding structured metadata or suggesting a resolver group—not privileged remediation.

Exit gate:

- identity, authorization, audit, rollback, and change control validated per action.

## KPI tree

### Outcome metrics

- time to correct priority;
- time to first useful response;
- P1 miss count and escalation delay;
- reassignment rate;
- first-contact resolution where appropriate;
- SLA breach attributable to triage;
- analyst productive capacity;
- stakeholder satisfaction.

### Quality metrics

- P1 precision and recall;
- macro F1 and calibration;
- groundedness;
- citation relevance;
- unsupported-claim rate;
- correct escalation rate;
- runbook retrieval recall;
- schema success;
- human-review compliance.

### Adoption metrics

- eligible users;
- active users;
- assisted ticket share;
- accepted unchanged;
- accepted after edit;
- rejected;
- training completion;
- feedback participation.

### Reliability and cost

- availability;
- latency;
- error and fallback rate;
- cost per triage;
- monthly budget variance;
- incident count;
- mean time to recover;
- rollback frequency.

## RACI example

| Activity | Sponsor | Product owner | ITSM owner | AI engineer | Security/privacy | Analysts | Platform/SRE |
|---|---|---|---|---|---|---|---|
| Define value and scope | A | R | C | C | C | C | I |
| Approve priority policy | I | C | A/R | C | C | C | I |
| Build model/prompt/RAG | I | C | C | A/R | C | C | C |
| Approve data use | I | C | C | C | A/R | I | C |
| Own runbooks | I | C | A/R | C | C | C | I |
| Pilot operation | I | A | R | R | C | R | R |
| Production SLO | I | A | C | C | C | I | R |
| Safety incident | I | C | C | R | A/R | I | R |

`A` = accountable, `R` = responsible, `C` = consulted, `I` = informed.

## Build-versus-buy considerations

### Build strengths

- organization-specific priority and runbook logic;
- full control over data, policy, evaluation, and integration;
- transparent learning and differentiation;
- provider portability.

### Build costs

- engineering and lifecycle ownership;
- evaluation burden;
- security and compliance work;
- ongoing knowledge and model maintenance.

### Buy strengths

- faster initial capability;
- vendor-supported integrations;
- managed operations and feature evolution.

### Buy risks

- limited transparency;
- data and residency constraints;
- vendor lock-in;
- hard-to-customize policy;
- cost scaling;
- unclear evaluation evidence.

A hybrid approach is likely: use managed model/platform capabilities while retaining organizational policy, evaluation, runbooks, identity, and audit controls.

## Decision statement

Proceed beyond a portfolio prototype only when the organization has:

- a measurable service problem;
- approved data and owners;
- a fixed evaluation benchmark;
- explicit safety and quality gates;
- shadow-mode evidence;
- a funded operating model;
- a manual fallback;
- a risk-adjusted value case.

The project demonstrates how to reach that decision responsibly; it does not manufacture a guaranteed ROI.
