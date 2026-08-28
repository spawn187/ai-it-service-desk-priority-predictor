# Live Demo Script

## Demo objective

Show in seven to ten minutes that the repository is an end-to-end, controlled AI engineering project—not a notebook and not an ungoverned chatbot.

The narrative should move from business problem to executable evidence, then to limitations and production design.

## Preparation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/generate_data.py --rows 30000 --seed 42
python scripts/train_model.py --data data/synthetic_tickets.csv
pytest -q
python scripts/run_prompt_evals.py --fail-on-regression
```

Start the applications in separate terminals:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
streamlit run app/streamlit_app.py
```

Open:

- repository README;
- Streamlit app;
- API `/docs`;
- `assets/copilot_architecture.svg`;
- `artifacts/prompt_eval_metrics.json`;
- `docs/THREAT_MODEL.md`.

## Seven-minute version

### 0:00-0:40 — Business problem

Say:

> I chose a problem that connects my IT operations and service-management background with applied AI. Manual ticket priority and first-response quality can vary, but a fully autonomous agent would be too risky. I therefore built a hybrid decision-support system: a transparent ML classifier predicts P1-P4, and a guarded RAG copilot creates a cited first-response plan. The analyst remains accountable.

Show the README summary and architecture image.

### 0:40-1:30 — Classical ML proof

Show the reference model table and confusion matrix.

Say:

> I generated 30,000 deterministic synthetic tickets because real service-desk data is sensitive. I compared logistic regression, linear SVM, and SGD. SVM had slightly better macro F1, but logistic regression had stronger P1 recall, native probabilities, and simpler explainability. That made it the better operational choice for confidence-based human review.

Be explicit:

> These metrics prove reproducibility on the synthetic benchmark, not production performance.

### 1:30-2:20 — Architecture and control boundaries

Show `assets/copilot_architecture.svg`.

Say:

> The important design decision is separation of concerns. The ML model predicts. The retriever supplies evidence. The prompt defines a bounded synthesis task. Pydantic validates the result. Application policy—not the model—enforces review and keeps automation disabled.

Point out:

- redaction before prompting;
- direct and indirect injection checks;
- stable evidence IDs;
- prompt version and hashes;
- post-generation citation filtering;
- no execution tools.

### 2:20-3:30 — Normal outage scenario

In Streamlit, select **Warehouse network outage** and run controlled triage.

Show:

- P1 prediction and confidence;
- human review required;
- retrieved network runbook sections;
- recommended read-only / evidence-gathering actions;
- escalation guidance;
- policy decisions;
- prompt and input hashes.

Say:

> Even for a high-confidence P1, the system never auto-escalates or changes infrastructure. It prepares a traceable plan and requires an incident manager or analyst to confirm severity.

### 3:30-4:30 — Prompt-injection and sensitive-data scenario

Select **Prompt injection and sensitive data**.

Show:

- email and password redaction count;
- injection flag;
- mandatory review;
- automation disabled;
- sanitized prompt audit.

Say:

> The ticket is not trusted. Redaction and injection detection happen before retrieval and prompt construction. A prompt instruction alone is not the security boundary; output validation and application policy are applied after generation too.

### 4:30-5:20 — Prompt engineering evidence

Open:

- `prompts/system_prompt_v1.md`;
- `prompts/response_schema.json`;
- `prompts/PROMPT_CHANGELOG.md`;
- `docs/PROMPT_ENGINEERING.md`.

Say:

> I treat prompts like code: versioned, reviewed, hashed, schema-constrained, and tested. The model can only cite evidence IDs supplied by retrieval. A provider adapter test deliberately tries to enable automation, use a fake citation, and change the prompt version; the application rejects those changes.

### 5:20-6:10 — Evaluation and CI

Show the GitHub Actions badge and `artifacts/prompt_eval_metrics.json`.

Say:

> CI runs linting, tests, an offline copilot smoke test, a model-training smoke test, and ten prompt/RAG contract cases. The 10/10 result is deliberately labeled as deterministic invariant testing, not a claim that an LLM is always correct.

### 6:10-7:00 — Production path and close

Open `docs/LLMOPS_EVALUATION.md` or `docs/THREAT_MODEL.md`.

Say:

> A real rollout begins with approved anonymized data, temporal validation, a fixed benchmark, shadow mode, analyst feedback, calibrated thresholds, identity and access controls, monitoring, and rollback. The project demonstrates that I can connect AI engineering with the operating model required to run it safely.

Close with:

> I did not design an isolated model. I designed a challengeable AI service: reproducible, grounded, testable, observable, and intentionally limited where the risk is higher than the proven value.

## Ten-minute technical version

Add the following sections.

### Code walkthrough

Open `src/it_ticket_priority/copilot/orchestrator.py`.

Explain the exact sequence:

1. request validation;
2. redaction and injection detection;
3. classical ML scoring;
4. query construction;
5. runbook retrieval;
6. retrieved-context scanning;
7. prompt package creation;
8. assistant/provider generation;
9. post-generation policy;
10. structured decision response.

Open `assistant.py` and highlight:

```python
"automation_allowed": False
```

and citation filtering against `valid_evidence_ids`.

### API walkthrough

Open `/docs`, select `POST /copilot/triage`, and submit `examples/copilot_request.json`.

Show that the response contains machine-consumable sections, not only prose.

### Test walkthrough

Open:

- `tests/test_llm_adapter.py`;
- `tests/test_indirect_prompt_injection.py`;
- `tests/test_prompt_evaluation.py`.

Explain that the fake provider behaves badly on purpose and the application still forces safe policy.

## Command-line fallback demo

When a browser or UI fails:

```bash
python scripts/run_copilot_demo.py
```

For the quality gate:

```bash
python scripts/run_prompt_evals.py --fail-on-regression
```

For API testing:

```bash
curl -X POST "http://localhost:8000/copilot/triage" \
  -H "Content-Type: application/json" \
  --data @examples/copilot_request.json
```

## Questions to invite

End with one of these:

- “Would you like me to defend the model choice, the prompt controls, or the production rollout first?”
- “The most interesting trade-off is why the application, not the LLM, owns policy. I am happy to go into that code path.”
- “I can also show how I would replace the local retriever or deterministic adapter without weakening the contract.”

## Questions and concise answers

### Is the offline assistant really AI?

The full project contains a trained ML classifier. The offline copilot adapter is intentionally deterministic so the orchestration and safety controls are reproducible without a paid provider. A provider-neutral LLM adapter is included and tested. I do not mislabel the deterministic fallback as an LLM.

### Why not use a transformer for priority?

The current task and synthetic benchmark are well served by linear NLP, and the operational requirements favor probability output, explainability, low latency, and low cost. A transformer should be benchmarked on approved real multilingual data before adding complexity.

### Does prompt-injection detection make the system secure?

No. It is one signal. The stronger controls are no execution tools, instruction/data separation, context filtering, structured validation, citation allowlisting, application-owned policy, human review, and monitoring.

### Why is every action marked as requiring approval?

Because this is a decision-support portfolio and does not have environment-specific identity, authorization, change, rollback, or safety controls for production actions.

### What would be the first production improvement?

Approved anonymized historical data and label audit, followed by temporal validation, probability calibration, and a fixed expert-reviewed benchmark in shadow mode.

## Demo mistakes to avoid

Do not say:

- “This model is 90% accurate in production.”
- “The system automatically resolves incidents.”
- “The prompt prevents all hallucinations.”
- “The 10/10 evaluation proves the LLM is perfect.”
- “These are company runbooks.”
- “I deployed this exact system at a former employer.”

Say instead:

- “The reference metric is reproducible on synthetic data.”
- “The system is decision support and keeps automation disabled.”
- “The controls reduce risk and make failures visible.”
- “The automated suite validates defined engineering invariants.”
- “The runbooks are representative portfolio content.”
- “The use case is informed by my domain experience, while the implementation is an independent portfolio project.”
