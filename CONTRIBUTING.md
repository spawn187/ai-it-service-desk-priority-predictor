# Contributing

Contributions are welcome when they preserve the repository's core principles: reproducibility, privacy, honest evaluation, least agency, human ownership, and production-minded engineering.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Before opening a pull request

```bash
ruff check .
pytest -q
python scripts/run_prompt_evals.py --fail-on-regression
python scripts/run_copilot_demo.py > /tmp/copilot_demo.json
python scripts/train_model.py --rows 1500 --quick \
  --model-path /tmp/priority_model.joblib \
  --metadata-path /tmp/model_metadata.json \
  --artifact-dir /tmp/artifacts \
  --asset-dir /tmp/assets
```

## General rules

- Do not commit real ticket data, personal data, secrets, internal company information,
  hostnames, tenant details, or confidential runbooks.
- Add or update tests for behavior changes.
- Keep training and inference preprocessing in the same serialized ML pipeline.
- Do not report metrics without a reproducible command and dataset configuration.
- Document limitations and trade-offs rather than optimizing only for headline scores.
- Keep the API backward compatible or clearly document version-breaking changes.
- Do not add autonomous execution tools without a separate architecture and security review.
- Do not present heuristic safety controls as guarantees.

## Prompt, schema, or RAG changes

1. Add or update a failing evaluation case that demonstrates the problem.
2. Decide whether the correct fix belongs in retrieval, prompt text, schema, application
   policy, runbook content, or data handling.
3. Change the smallest effective layer.
4. Increment the prompt version when behavior changes.
5. Update `prompts/PROMPT_CHANGELOG.md` with the rationale.
6. Run the deterministic prompt/RAG suite.
7. Manually review representative outputs for usefulness and unintended regressions.
8. Update documentation when the output contract or operating policy changes.

## Knowledge-base changes

- Use representative public portfolio content only.
- Prefer read-only, reversible diagnostic guidance.
- State escalation criteria and prohibited autonomous actions.
- Keep stable document IDs when possible.
- Add an evaluation case when a new service domain is introduced.
- Treat every runbook as untrusted content at runtime even when it is reviewed in source
  control.

## Model changes

- Compare against the current baseline on the same split and metrics.
- Explain why the selected model better fits the operating objective.
- Report P1 precision and recall, not only accuracy.
- Preserve reproducibility and model metadata.
- Do not commit an opaque binary as the only way to reproduce results.
