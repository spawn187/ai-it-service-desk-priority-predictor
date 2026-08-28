# Reference Frameworks and Primary Guidance

This portfolio uses the following authoritative sources as design references. They inform the architecture and evaluation strategy; they do not constitute certification or formal compliance.

## NIST

### AI Risk Management Framework: Generative AI Profile (NIST AI 600-1)

- Publication page: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- DOI: https://doi.org/10.6028/NIST.AI.600-1

Applied themes:

- lifecycle risk management;
- governance and ownership;
- measurement and evaluation;
- transparency and documentation;
- human oversight;
- monitoring and incident response;
- trustworthy and responsible AI considerations.

## OWASP GenAI Security Project

### OWASP GenAI LLM Top 10 2026

- Resource page: https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/

Applied themes:

- prompt injection and indirect injection;
- sensitive-information disclosure;
- excessive agency;
- output handling;
- system-prompt and knowledge-source risks;
- supply-chain and operational security;
- defense in depth rather than prompt-only controls.

## Microsoft Architecture and Foundry guidance

### RAG prompt engineering

- https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-prompt-engineering

Applied themes:

- system, scenario instruction, context, and query separation;
- explicit grounding constraints;
- source identifiers and citations;
- insufficient-context behavior;
- top-k and relevance thresholds;
- prompt and end-to-end evaluation.

### Generative AI observability in Microsoft Foundry

- https://learn.microsoft.com/en-us/azure/foundry/concepts/observability

Applied themes:

- pre-production evaluation;
- production monitoring;
- quality, safety, operational, and business signals;
- traceability across application components;
- iterative improvement and release governance.

## Project mapping

| Reference theme | Portfolio implementation |
|---|---|
| Governance and lifecycle | Case study, business case, LLMOps plan, RACI, ADRs |
| Prompt injection | Direct detector, retrieved-context scan, untrusted-data boundaries |
| Sensitive information | Pre-prompt redaction and regression tests |
| Excessive agency | No tools, mandatory approval, application-forced automation off |
| Grounding | Runbook retrieval, stable evidence IDs, citation allowlist |
| Structured output | Pydantic model and JSON Schema |
| Evaluation | ML metrics, deterministic prompt/RAG suite, manual rubric |
| Observability | Proposed service, retrieval, ML, generative, safety, adoption metrics |
| Incident and rollback | Feature disablement, versioned rollback units, manual continuity |

## Interpretation

The project demonstrates practical alignment with selected principles. A real deployment would require organization-specific legal, privacy, security, architecture, risk, and audit assessment.
