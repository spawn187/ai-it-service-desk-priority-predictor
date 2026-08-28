# Portfolio Case Study: Guarded AI Service Desk Copilot

## Executive summary

This project demonstrates how an experienced IT operations and service-management practitioner can convert a familiar operational problem into a controlled AI product.

The system supports service-desk analysts in two distinct decisions:

1. **How urgent is the ticket?** A classical machine-learning model predicts P1-P4 priority from ticket text and operational metadata.
2. **What should the analyst do first?** A retrieval-grounded copilot creates a safe, structured first-response plan using approved runbooks.

The design deliberately avoids the common portfolio shortcut of sending the entire problem to a large language model. Priority classification remains transparent and measurable, while the generative layer is limited to synthesis, uncertainty communication, and evidence-grounded recommendations. The application—not the model—owns policy.

## Business problem

Manual ticket prioritization and first-response planning can be inconsistent across analysts, shifts, locations, and service domains.

Potential consequences include:

- a real major incident being under-prioritized;
- excessive P1 assignments and alert fatigue;
- delayed escalation because scope and impact were not captured;
- first-response steps that are not linked to approved runbooks;
- undocumented assumptions and missing evidence;
- sensitive values being copied into AI prompts;
- automation bias when generated text sounds more certain than the evidence supports.

The project therefore optimizes for **decision quality and control**, not only prediction accuracy or fluent text.

## Target users and stakeholders

| Stakeholder | Need | Project response |
|---|---|---|
| Service-desk analyst | Faster, consistent first response | Priority, confidence, grounded actions, missing-information checklist |
| Incident manager | Reliable major-incident escalation | P1-focused ML objective and mandatory analyst confirmation |
| Service owner | Traceability to operational knowledge | Runbook evidence IDs and source paths |
| Security team | No autonomous containment or unsafe data handling | Security review gate, evidence preservation, redaction, no execution tool |
| IT operations lead | Measurable quality and rollback | CI evaluation, model metadata, prompt hashes, monitoring design |
| Risk / compliance | Explainable controls and ownership | Threat model, model card, audit trail, explicit limitations |
| Product / transformation lead | Staged value realization | Shadow-mode rollout, adoption metrics, business-case framework |

## Success criteria

### Offline engineering criteria

- The full solution can run without external API keys.
- Synthetic data generation and ML training are reproducible.
- Preprocessing is fitted only on training data.
- The selected model provides probabilities and inspectable feature contributions.
- Sensitive values are masked before retrieval and prompt construction.
- Direct and indirect prompt-injection signals trigger review.
- Generated output must validate against a strict schema.
- Citations may reference only retrieved evidence IDs.
- Application policy always disables autonomous execution.
- Prompt/RAG regression failures block CI.

### Pilot criteria for a real organization

These are proposed gates, not claimed results:

- approved anonymized historical dataset and label-quality review;
- temporal validation rather than only a random split;
- agreed P1 miss-cost and false-escalation cost;
- probability calibration and threshold approval;
- analyst override reason captured;
- documented service ownership and escalation paths;
- security, privacy, legal, architecture, and operations approval;
- shadow-mode comparison before workflow impact;
- manual continuity path and rollback tested.

## Discovery and requirements

The project starts from the operating process rather than the algorithm.

### Functional requirements

- Accept ticket text and operational metadata.
- Predict P1-P4 priority and probabilities.
- Explain the largest positive local feature contributions.
- Retrieve relevant runbook sections.
- Produce a concise first-response plan with escalation guidance.
- Separate assumptions from missing information.
- Show citations, guardrails, policy decisions, and prompt audit data.
- Expose both prediction and copilot workflows through API and UI.

### Non-functional requirements

- Reproducible and inspectable without cloud spend.
- Fast enough for interactive service-desk use.
- No committed confidential data or model binary.
- Provider-neutral generative interface.
- Structured, machine-validated output.
- Deterministic automated evaluation for safety-critical invariants.
- Clear failure behavior when the model or evidence is unavailable.
- No autonomous system-changing capability.

## Solution architecture

The architecture contains four policy boundaries.

### 1. Input boundary

Pydantic validates the request and rejects unexpected fields. The security module normalizes Unicode, removes control characters, masks common sensitive patterns, truncates oversized text, and records redaction events.

### 2. Prediction boundary

The classical pipeline combines:

- TF-IDF unigrams and bigrams for ticket descriptions;
- one-hot encoding for category, channel, service criticality, and site;
- imputation and scaling for numerical and Boolean signals;
- a balanced logistic-regression classifier.

All transformations remain in one scikit-learn pipeline, reducing leakage risk and keeping training and inference behavior aligned.

### 3. Retrieval and prompt boundary

The local retriever indexes approved Markdown runbook sections. Each returned fragment has a stable evidence ID, document ID, source path, score, and excerpt.

The prompt builder keeps three layers separate:

- **system:** non-negotiable behavior and safety constraints;
- **developer:** task, evidence rules, and response schema;
- **user/data:** serialized ticket, prediction, guardrail state, and retrieved context, explicitly marked untrusted.

The complete prompt package carries an input SHA-256 and prompt SHA-256 for reproducibility and audit comparison.

### 4. Output and policy boundary

Any provider output must validate against `CopilotAdvice`. The adapter removes citations that were not supplied by the retriever and then re-applies application policy:

- mandatory review cannot be disabled by the model;
- autonomous execution cannot be enabled by the model;
- the prompt version is set from trusted application state;
- P1, security, injection, context-injection, low-confidence, and weak-grounding rules remain authoritative.

## Data and ML design

### Why synthetic data

Public service-desk tickets can expose personal information, identities, tenant details, hostnames, service architecture, vulnerabilities, business processes, and security events. A deterministic generator lets the repository remain public and reproducible.

The generator introduces class imbalance, missing values, duplicates, typographical noise, and imperfect relationships between text and labels. This is more useful than a perfectly separable toy dataset, but it is still simpler than real language.

### Leakage controls

- Data is split before the vectorizer, encoder, imputer, or scaler is fitted.
- All transformations are inside a single pipeline.
- Post-decision fields are excluded.
- Reference results are measured on a holdout set.
- The production roadmap requires temporal validation and approved real data.

### Model selection

Three linear candidates were compared. Linear SVM had slightly stronger macro F1, but balanced logistic regression was selected because it combined strong P1 recall with native probabilities and interpretable coefficients.

This is an operating-model decision, not a leaderboard decision. Confidence-based routing and analyst review require usable probability estimates, while P1 recall reflects the asymmetric cost of missing a major incident.

## Prompt and RAG design

### Weak baseline

A typical baseline would say: “You are an IT support expert. Read this ticket and recommend next steps.” That prompt fails to define:

- which content is instruction versus data;
- whether retrieved text is trusted;
- what output contract is required;
- which sources may be cited;
- how uncertainty should be represented;
- whether the model may claim actions were executed;
- which actions require approval;
- how regressions are detected.

### Engineered version

The production prompt adds:

- explicit instruction hierarchy;
- untrusted-input markers;
- a machine-generated JSON Schema;
- evidence-ID allowlisting;
- facts / assumptions / missing-information separation;
- least-agency language;
- no-execution claims;
- mandatory approval;
- prompt versioning and hashes;
- deterministic contract evaluation.

The prompt is therefore one component inside a defense-in-depth workflow rather than the only control.

## Safety and Responsible AI controls

| Risk | Control | Residual limitation |
|---|---|---|
| Personal or credential data enters a prompt | Pattern redaction before retrieval and prompting | Pattern matching cannot detect every sensitive value |
| Ticket contains prompt injection | Direct signal detector and human-review gate | Novel or obfuscated attacks may evade detection |
| Runbook contains malicious instructions | Context scan and removal of flagged evidence | Detection remains heuristic |
| Model invents a citation | Citation allowlist and post-generation filtering | A valid citation can still be semantically weak |
| Model enables automation | Application forcibly sets `automation_allowed=false` | Real deployments still need authorization and tool controls |
| Confident but wrong advice | Evidence, uncertainty fields, missing information, human review | Analysts can still exhibit automation bias |
| Priority bias or drift | Segmented metrics, overrides, delayed labels, retraining gates | Real performance depends on label and population quality |
| Provider outage or cost spike | Offline fallback and provider-neutral interface | Deterministic fallback is less expressive than an LLM |

## Evaluation strategy

### ML evaluation

- accuracy and macro F1;
- P1 precision and recall;
- confusion matrix;
- candidate comparison;
- local feature contributions;
- data-quality report and experiment metadata.

### Prompt/RAG contract evaluation

The automated suite currently checks:

- direct injection detection;
- sensitive-data redaction;
- expected runbook retrieval;
- minimum citation count;
- human-review policy;
- no autonomous execution;
- instruction/data separation;
- structured output and prompt-version preservation;
- absence of a raw email from the final prompt.

The suite result is 10/10 on the checked-in reference cases. It is described accurately as a deterministic contract test, not as an overall LLM-quality score.

### Manual evaluation

A production evaluation would additionally score:

- factual grounding;
- operational usefulness;
- completeness of first-response questions;
- severity and escalation appropriateness;
- unsupported-claim rate;
- citation relevance;
- clarity and concision;
- harmful-action suggestions;
- multilingual quality;
- consistency across repeated runs.

## Delivery and operating model

### Interfaces

- FastAPI for machine integration and OpenAPI inspection;
- Streamlit for an interview-friendly interactive demonstration;
- CLI scripts for deterministic reproduction;
- Docker for portable runtime packaging;
- GitHub Actions for lint, tests, prompt evaluation, offline copilot smoke test, and ML training smoke test.

### Proposed real rollout

1. **Research sandbox:** approved data sample, label review, threat modeling.
2. **Offline benchmark:** ML and generative-provider comparison against fixed cases.
3. **Shadow mode:** score live tickets but make no workflow changes.
4. **Analyst assist:** display suggestions with evidence and mandatory confirmation.
5. **Constrained integration:** only approved low-risk routing or enrichment actions.
6. **Operational service:** ownership, SLOs, monitoring, incident process, cost controls, release calendar, rollback.

## Business-value hypothesis

The value proposition is not “replace the service desk.” It is:

- reduce time spent assembling the first response;
- increase consistency of impact capture and escalation;
- improve runbook usage and traceability;
- make uncertainty and missing information visible;
- provide a measurable feedback loop through analyst overrides;
- create a controlled foundation for future automation.

The repository includes an assumption-based calculator in `BUSINESS_CASE.md`. No savings are claimed without organizational data.

## What is genuinely demonstrated

A reviewer can inspect and run evidence for:

- Python software engineering;
- supervised NLP classification;
- feature engineering and model evaluation;
- explainable inference;
- API and UI delivery;
- Docker and CI;
- prompt engineering as versioned code;
- RAG and citation controls;
- LLM output validation;
- injection and sensitive-data guardrails;
- LLMOps evaluation and release gates;
- AI product, governance, and operating-model thinking;
- ITSM and Microsoft-cloud domain translation.

## What is not claimed

- The reference model is not trained on an employer's real tickets.
- The metrics do not prove production generalization.
- The runbooks are representative examples, not a company's approved procedures.
- The deterministic adapter is not a large language model.
- The system has not autonomously changed production services.
- The repository is not evidence of a completed enterprise rollout.

These boundaries make the project more credible, not less.

## Defensible architecture decisions

The repository contains explicit Architecture Decision Records:

- [ADR-001: Hybrid classical ML and generative copilot](adr/001-hybrid-ml-and-copilot.md)
- [ADR-002: Human-in-the-loop and no autonomous execution](adr/002-human-in-the-loop.md)
- [ADR-003: Local inspectable retrieval before vector infrastructure](adr/003-local-retrieval.md)
- [ADR-004: Deterministic offline quality gate](adr/004-deterministic-evaluation.md)

## Suggested review path

A technical reviewer can validate the project in this order:

1. Read the README business problem and reference metrics.
2. Inspect `pipeline.py`, `train.py`, and `inference.py`.
3. Inspect `security.py`, `retrieval.py`, `prompting.py`, and `orchestrator.py`.
4. Read `system_prompt_v1.md` and `response_schema.json`.
5. Run `scripts/run_prompt_evals.py --fail-on-regression`.
6. Open the Streamlit copilot page and test outage, identity, security, and injection scenarios.
7. Inspect the API contract at `/docs`.
8. Read the threat model, model card, and ADRs.
9. Challenge the limitations and production rollout assumptions.

## Closing position

The strongest part of the project is not one model, prompt, or screenshot. It is the separation of concerns:

- the ML model predicts;
- the retriever supplies evidence;
- the prompt defines a constrained task;
- the schema validates structure;
- the application enforces policy;
- the analyst owns the decision;
- CI protects known invariants;
- monitoring and governance own the production lifecycle.

That is the difference between a chatbot demonstration and an AI service that can be evaluated, challenged, and operated responsibly.
