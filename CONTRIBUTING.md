# Contributing

Contributions are welcome when they preserve the repository's core principles: reproducibility, privacy, honest evaluation, and production-minded engineering.

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
python scripts/train_model.py --rows 1500 --quick \
  --model-path /tmp/priority_model.joblib \
  --metadata-path /tmp/model_metadata.json \
  --artifact-dir /tmp/artifacts \
  --asset-dir /tmp/assets
```

## Contribution rules

- Do not commit real ticket data, personal data, secrets, or internal company information.
- Add or update tests for behavior changes.
- Keep training and inference preprocessing in the same serialized pipeline.
- Do not report metrics without a reproducible command and dataset configuration.
- Document limitations and trade-offs rather than optimizing only for headline scores.
- Keep the API backward compatible or clearly version breaking changes.
