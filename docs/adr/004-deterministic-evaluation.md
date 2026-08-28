# ADR-004: Use deterministic offline evaluation as a mandatory CI gate

- **Status:** Accepted
- **Date:** 2026-08-28

## Context

A portfolio should be reproducible without provider credentials or usage cost. Several critical behaviors—redaction, injection handling, evidence retrieval, schema validation, citation filtering, and review policy—should not depend on model sampling.

## Decision

Create a deterministic offline assistant and fixed prompt/RAG cases. Run them in CI with `--fail-on-regression`. Keep external generative-quality evaluation as a separate future layer.

## Rationale

- fast and inexpensive on every pull request;
- stable results;
- isolates application and prompt-contract regressions;
- prevents an unavailable provider from blocking local verification;
- avoids misrepresenting provider output as the only evidence of engineering quality.

## Consequences

### Positive

- reproducible quality gate;
- no secrets in CI;
- clear failure messages;
- easy extension through JSONL cases;
- architecture can be tested before choosing a provider.

### Negative

- does not measure fluency, nuanced groundedness, or open-ended usefulness;
- deterministic outputs can be easier than real model behavior;
- external provider integration still needs a benchmark and expert review.

## Interpretation rule

The current 10/10 result may be described only as deterministic contract compliance on the checked-in cases. It must not be presented as production LLM accuracy or general safety proof.
