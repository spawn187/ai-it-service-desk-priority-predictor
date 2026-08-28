# ADR-002: Keep humans in the loop and disable autonomous execution

- **Status:** Accepted
- **Date:** 2026-08-28

## Context

Service-desk actions can affect identity, access, network, security, availability, data, and business operations. A generated recommendation is not authorization and cannot establish that a change is safe in a specific environment.

## Decision

The portfolio system remains advisory. It exposes no execution tool, marks every recommended action as requiring approval, and forces `automation_allowed=false` after generation.

Mandatory human review applies to:

- P1 predictions;
- low-confidence predictions;
- security-related tickets;
- direct or indirect prompt-injection signals;
- cases without relevant evidence.

## Rationale

- prompt text is not an authorization mechanism;
- the portfolio lacks environment-specific identity, RBAC, change, rollback, and safety controls;
- analyst judgment is required for impact, context, and business trade-offs;
- limiting agency reduces the impact of hallucination and injection;
- the design remains credible and safe to demonstrate publicly.

## Consequences

### Positive

- reduced operational risk;
- clear accountability;
- safer failure behavior;
- easier adoption in shadow and assist modes;
- model/provider cannot silently expand its authority.

### Negative

- lower maximum automation benefit;
- analyst effort remains necessary;
- acceptance and override UX becomes important;
- business value must be proven through decision quality and time reduction.

## Future reassessment

A specific low-risk action may be assessed separately only with typed tools, least-privilege identity, policy-as-code, explicit approval, dry run, audit, idempotency, rollback, rate limits, and operational ownership.
