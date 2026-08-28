# ADR-003: Start with local, inspectable TF-IDF retrieval

- **Status:** Accepted
- **Date:** 2026-08-28

## Context

The reference knowledge base is a small set of curated Markdown runbooks. A vector database would add infrastructure, credentials, cost, deployment, and monitoring without evidence that semantic scale requires it.

## Decision

Use an in-process TF-IDF retriever over runbook sections. Return stable evidence IDs, source paths, excerpts, and transparent similarity scores behind a replaceable interface.

## Rationale

- fully offline and reproducible;
- no cloud account or API key;
- easy to inspect during an interview;
- sufficient for a small domain corpus;
- transparent failure analysis;
- lower operational complexity;
- clean migration path to hybrid or vector retrieval.

## Consequences

### Positive

- simple setup;
- deterministic behavior;
- low latency and cost;
- easy CI evaluation;
- corpus remains version-controlled with application code.

### Negative

- weaker semantic matching and multilingual coverage;
- limited scalability;
- no built-in document-level authorization;
- vocabulary dependence;
- no enterprise knowledge connectors.

## Migration triggers

Reassess when measured evidence shows:

- corpus scale materially degrades retrieval;
- multilingual or paraphrase recall is insufficient;
- document authorization requires an external search platform;
- hybrid keyword/vector ranking improves a fixed benchmark;
- freshness and connector requirements exceed local files.
