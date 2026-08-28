# Security Policy

## Supported version

The latest `main` branch is the supported portfolio version.

## Reporting a vulnerability

Do not publish sensitive vulnerability details, working exploits, credentials, or private data in a public issue. Contact the repository owner privately through the GitHub profile associated with this repository.

## Data policy

This repository must never contain:

- real service-desk exports;
- personal or customer information;
- credentials, API keys, access tokens, or connection strings;
- internal hostnames, IP inventories, tenant identifiers, or architecture diagrams;
- confidential incident descriptions;
- employer-owned prompts, runbooks, policies, or model artifacts.

All checked-in tickets and runbooks are synthetic or representative portfolio content.

## AI-specific security policy

- Ticket text and retrieved documents are untrusted data.
- No prompt is treated as an authorization mechanism.
- The portfolio implementation must not expose autonomous production tools.
- `automation_allowed` remains false at the application-policy layer.
- Citations must be filtered against the evidence IDs supplied by retrieval.
- Provider output must validate against the structured response contract.
- Changes to prompt, schema, retrieval, or safety policy require regression testing.
- Injection and redaction controls are risk-reduction mechanisms, not guarantees.

## Production warning

The included API is a public portfolio implementation. Before production use, add and validate:

- authenticated access and role/tenant authorization;
- private networking, TLS, WAF, rate limits, and payload limits;
- enterprise DLP/redaction and data minimization;
- managed identity, secret management, and rotation;
- redacted structured audit logging and approved retention;
- dependency, container, code, and secret scanning;
- signed artifacts, image provenance, and SBOM;
- provider data-residency and contractual controls;
- model, prompt, corpus, and schema release governance;
- monitoring, incident response, feature disablement, and rollback;
- manual continuity when AI components are unavailable.

See [Threat Model](docs/THREAT_MODEL.md) for the detailed risk register.
