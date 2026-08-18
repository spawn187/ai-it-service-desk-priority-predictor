.PHONY: install install-dev data train quick-train api dashboard test lint format docker clean

install:
	python -m pip install -e .

install-dev:
	python -m pip install -e ".[dev]"

data:
	python scripts/generate_data.py --rows 30000

train:
	python scripts/train_model.py --rows 30000

quick-train:
	python scripts/train_model.py --rows 3000 --quick

api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dashboard:
	streamlit run app/streamlit_app.py

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .

docker:
	docker compose up --build

clean:
	rm -rf .pytest_cache .ruff_cache htmlcov mlruns
	rm -f data/synthetic_tickets.csv
