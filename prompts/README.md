# Prompt engineering assets

This directory is intentionally versioned like application code. It demonstrates that prompt engineering is not a one-off text-writing exercise but a controlled engineering discipline.

## Design choices

- **Instruction/data separation:** system and developer rules are kept apart from ticket and retrieved content.
- **Structured output:** the assistant must return the JSON contract in `response_schema.json`.
- **Grounding:** citations may reference only evidence IDs supplied by the retriever.
- **Least agency:** the assistant has no execution tool and `automation_allowed` is always false.
- **Defense in depth:** PII/secret redaction, direct injection detection, retrieved-context scanning, output validation, citation filtering, and mandatory human-review gates.
- **Versioning:** prompt version `1.1.0` is hashed into every prompt package and preserved in validated output.
- **Evaluation:** deterministic contract tests run in CI; the manual rubric covers dimensions that require expert review or a model judge.

## Files

- `baseline_prompt_v0.md` — rejected weak baseline for design comparison.
- `system_prompt_v1.md` — stable non-negotiable behavior.
- `response_schema.json` — machine-validated output contract.
- `few_shot_examples.jsonl` — examples for a future external-model adapter.
- `PROMPT_CHANGELOG.md` — rationale for prompt evolution.

The offline fallback does not pretend to be an LLM. Its purpose is to make the complete orchestration, safety, retrieval, schema, and evaluation workflow reproducible without API keys or usage costs.
