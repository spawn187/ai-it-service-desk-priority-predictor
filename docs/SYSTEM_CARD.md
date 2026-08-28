# System Card: AI-Powered IT Service Desk Copilot

## System identity

- **Name:** AI-Powered IT Service Desk Copilot
- **Portfolio version:** 2.0.0
- **Prompt version:** 1.1.0
- **Purpose:** Human-reviewed IT service-desk priority and first-response decision support
- **Status:** Public reference implementation; not production deployed

## Intended users

- service-desk analysts;
- incident managers;
- IT operations and service owners;
- AI/ML, LLMOps, architecture, security, and product reviewers;
- interviewers evaluating applied AI engineering capability.

## Intended uses

- demonstrate P1-P4 text/metadata classification;
- retrieve representative runbook evidence;
- produce a safe, structured first-response plan;
- expose assumptions, missing information, escalation, and citations;
- demonstrate prompt engineering, safety controls, evaluation, and operating model;
- support offline learning and portfolio review.

## Out-of-scope uses

- automatic remediation or privileged operations;
- replacing an incident manager or security responder;
- production decisions without organizational validation;
- processing real confidential tickets in the public repository;
- medical, legal, financial, physical-safety, or non-IT decision making;
- employee performance or disciplinary decisions;
- unattended cross-tenant processing.

## System components

- synthetic ticket generator and data validation;
- TF-IDF and metadata ML pipeline;
- balanced logistic-regression production candidate;
- local runbook retriever;
- input redaction and injection signal detector;
- versioned prompt and JSON Schema;
- offline deterministic assistant;
- provider-neutral structured LLM adapter;
- output validation and application policy;
- FastAPI, Streamlit, Docker, tests, CI, and documentation.

## Data

### Training and evaluation

The public ML reference uses generated tickets. No employer, employee, customer, or production data is included.

### Knowledge base

The runbooks are representative public portfolio content written for the project. They are not official procedures for any organization.

### Runtime input

The API accepts ticket descriptions and structured metadata. The application masks common sensitive patterns before retrieval and prompt construction, but pattern detection is not complete.

## Reference performance

### ML

Reference holdout on synthetic data:

- accuracy: 85.53%;
- macro F1: 83.16%;
- P1 precision: 70.90%;
- P1 recall: 90.87%.

These values do not establish performance on real organizational tickets.

### Prompt/RAG contracts

The checked-in deterministic suite records 10/10 passed. It validates defined engineering invariants, not open-ended LLM quality or complete security.

## Human oversight

The application requires review for P1, low-confidence, security, injection-flagged, context-injection, and no-evidence cases. All recommendations are advisory, every action requires approval, and automation is disabled.

## Safety controls

- request schema and bounds;
- normalization and input truncation;
- email, phone, identifier, and secret-pattern redaction;
- direct prompt-injection signals;
- retrieved-context injection scan;
- instruction/data separation;
- strict response schema;
- evidence-ID citation allowlist;
- provider-output validation;
- application-owned review and no-automation policy;
- no execution tools;
- deterministic regression tests;
- manual continuity and proposed rollback.

## Known limitations

- synthetic language is less varied than real tickets;
- labels are generated rather than analyst-adjudicated;
- local TF-IDF retrieval has limited semantic and multilingual coverage;
- pattern-based redaction and injection detection can miss cases;
- a valid evidence ID does not guarantee claim-level support;
- deterministic advice is less capable than an evaluated generative model;
- provider integration requires organization-specific controls;
- API authentication and enterprise platform controls are not part of the public demo;
- self-reported advice confidence is not a calibrated probability;
- analyst automation bias remains possible.

## Misuse risks

- presenting synthetic metrics as production evidence;
- treating recommendations as approved changes;
- pasting real secrets into the public demo;
- exposing the API without authentication;
- adding execution tools without authorization architecture;
- assuming prompt instructions alone prevent injection or hallucination;
- using outdated runbooks;
- silently removing human review.

## Monitoring requirements for production

- service health, latency, error, fallback, and cost;
- input, redaction, and injection distributions;
- retrieval score, no-evidence rate, and corpus freshness;
- priority, confidence, calibration, P1 performance, and overrides;
- schema success, citation relevance, unsupported claims, and safety events;
- analyst acceptance/edit/reject and business outcomes;
- segmented results by service, site, channel, language, and impact.

## Change management

Prompt, model, schema, retriever, corpus, policy, and provider are independently versioned release units. Behavior changes require tests, benchmark comparison, review, release notes, and rollback planning.

## Responsible disclosure

Security issues should be reported privately according to `SECURITY.md`.

## Contact

Repository owner: Norbert Komaromi / GitHub `spawn187`.
