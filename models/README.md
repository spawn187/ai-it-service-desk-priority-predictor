# Models

Trained binary model artifacts are intentionally not committed to Git. This keeps the repository lightweight and forces the demo to remain reproducible from source.

Generate `priority_model.joblib` and refresh `model_metadata.json` with:

```bash
python scripts/generate_data.py --rows 30000 --seed 42
python scripts/train_model.py --data data/synthetic_tickets.csv
```

The committed `model_metadata.json` records the reference experiment configuration and holdout metrics. The API and Streamlit app expect `models/priority_model.joblib`; train the model once before launching them.
