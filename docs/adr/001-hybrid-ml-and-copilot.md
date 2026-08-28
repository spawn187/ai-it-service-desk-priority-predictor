# ADR-001: Use a hybrid classical ML and generative copilot architecture

- **Status:** Accepted
- **Date:** 2026-08-28

## Context

The use case contains two different problems:

1. assigning one of four priority classes;
2. synthesizing a safe first-response plan from operational knowledge.

Using one generative model for both would reduce transparency and make probability calibration, repeatability, and cost harder to defend.

## Decision

Use a classical supervised NLP model for P1-P4 prediction and a separate retrieval-grounded generative interface for first-response synthesis.

## Rationale

- Priority is a bounded classification task.
- Classical linear models are fast, inexpensive, inspectable, and easy to benchmark.
- Native probabilities support confidence-based routing.
- The generative layer adds value where flexible synthesis is useful.
- Separate components can be evaluated, replaced, rolled back, and monitored independently.
- The application can combine their outputs under one policy layer.

## Consequences

### Positive

- clearer responsibility and failure analysis;
- lower inference cost for classification;
- easier explanation and reproducibility;
- provider portability;
- independent release and rollback;
- less pressure to give an LLM unnecessary authority.

### Negative

- more components and interfaces;
- two evaluation lifecycles;
- potential inconsistency between classifier and generated advice;
- additional orchestration code.

## Alternatives considered

### LLM-only classification and advice

Rejected for the reference design because it adds variance, cost, and weaker calibration to a simple classification task.

### Classical ML only

Rejected because it cannot flexibly synthesize grounded first-response guidance and missing-information questions.

### Rules only

Useful as a baseline and policy layer, but insufficient for the language variation and multi-signal classification objective.
