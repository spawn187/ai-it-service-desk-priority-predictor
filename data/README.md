# Data

The repository does not commit the full generated training CSV. Recreate it deterministically with:

```bash
python scripts/generate_data.py --rows 30000 --seed 42
```

The generated file is written to `data/synthetic_tickets.csv` and is ignored by Git. A 25-row sample remains under `data/sample/` for quick inspection.

No real company, customer, employee, or service desk data is included.
