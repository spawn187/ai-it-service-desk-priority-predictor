# Interview Talk Track

## 30-second version

I built an end-to-end machine learning system for IT service desk prioritization. It combines TF-IDF ticket text with operational metadata and predicts P1 to P4. I generated 30,000 reproducible synthetic tickets so the project contains no confidential data, compared three linear classifiers, and selected logistic regression for its 90.87% P1 recall, probability output, and explainability. I then exposed it through FastAPI and Streamlit, containerized it, added automated tests and GitHub Actions, and documented monitoring, drift, security, and human-review controls.

## 90-second version

The problem I chose is inconsistent manual ticket prioritization. A missed P1 can delay a critical response, but excessive P1 predictions create alert fatigue. I treated it as a cost-sensitive multi-class classification problem.

The input contains ticket text plus category, channel, service criticality, site, affected-user count, outage and security indicators, business-hours status, and related-incident volume. I built a single scikit-learn pipeline so TF-IDF, one-hot encoding, imputation, scaling, and the classifier are fitted only on training data. I compared balanced logistic regression, linear SVM, and SGD. Linear SVM had a slightly higher macro F1, but logistic regression achieved higher P1 recall and gave me probabilities for confidence-based routing. On a 6,000-ticket holdout set, it achieved 85.53% accuracy and 90.87% P1 recall.

The API never treats the model as the final authority. Every P1 and every prediction below 65% confidence requires analyst review. The repo also includes coefficient-based explanations, Docker, CI, tests, optional MLflow, and a production hardening plan. The important part is not just the model; it is the decision policy and the operational controls around it.

## Architecture decisions to defend

### Why TF-IDF instead of a transformer?

For this prototype, ticket descriptions are short and contain strong domain phrases. TF-IDF is fast, transparent, inexpensive, and performs well with a relatively small labeled dataset. A transformer would add infrastructure, tuning, explainability, and monitoring complexity. I would benchmark one when representative real data shows that semantic context or multilingual coverage justifies the cost.

### Why logistic regression when SVM had a slightly higher macro F1?

The production requirement was not simply to maximize one aggregate metric. Logistic regression produced higher P1 recall, native probabilities, and easy coefficient inspection. Those capabilities support confidence thresholds, human review, and explanation. I chose the model that best fits the operating model, not the model that wins one leaderboard column.

### Why optimize P1 recall?

A false negative on a critical outage can be much more expensive than a false positive that sends a ticket to analyst review. I used class weights to represent that asymmetry. I still track P1 precision because too many false escalations would create alert fatigue.

### How did you avoid leakage?

The split occurs before fitting the vectorizer, encoder, imputer, or scaler. All preprocessing is inside a pipeline. I also excluded post-decision fields such as SLA outcome, resolver group, resolution code, and manual override because they would not exist at scoring time.

### Why synthetic data?

Real service desk data contains personal and operationally sensitive information. Synthetic data makes the project public, deterministic, and safe. I am explicit that the metrics are not evidence of production performance. The next gate is validation on approved anonymized historical data.

## Likely technical questions

### What would you monitor?

I would monitor API availability, latency, errors, missingness, input distributions, vocabulary drift, predicted-priority distribution, confidence, analyst override rate, and delayed labeled metrics. P1 recall and false-negative count are the most important outcome metrics.

### How would you detect model drift?

I would compare current and baseline distributions for structured features and prediction probabilities, track out-of-vocabulary or text-embedding shift, and analyze performance when delayed labels arrive. Drift alerts should trigger investigation, not automatic retraining without approval.

### How would you deploy it safely?

First in shadow mode: the model scores tickets but does not change workflow. I would compare predictions with analyst decisions, review disagreements, calibrate probabilities, approve thresholds, then move to decision support. Automatic workflow changes would be limited, reversible, audited, and protected by fallback to manual triage.

### How would you improve it?

The next improvements would be real-data label auditing, probability calibration, cost-based thresholds, domain-specific text normalization, multilingual support, richer service and asset context, PII redaction, model registry integration, drift dashboards, and canary deployment.

### How would you scale it?

Inference is lightweight and stateless, so the API can scale horizontally. The model can be loaded once per worker, and batch or asynchronous scoring can be added for peaks. I would separate the dashboard from the API and obtain artifacts from a registry rather than baking mutable state into containers.

### What are the biggest risks?

The biggest risks are label inconsistency, distribution shift, confidential text, automation bias, false escalations, and missed P1 incidents. The controls are data governance, segmented testing, human confirmation, audit logs, monitoring, rollback, and clear ownership.

## Honest limitations to state

Do not pretend the synthetic metrics prove production readiness. Say this directly:

> The repository proves that I can design and implement the complete ML engineering workflow. It does not prove that the model will achieve the same metrics on a real organization’s tickets. That requires approved real data, label auditing, temporal testing, calibration, and a controlled pilot.

That answer is stronger than overselling the project.

## Live demo order

1. Open the README and explain the business problem.
2. Show the architecture diagram and repository structure.
3. Open `data_generator.py` and explain reproducibility and privacy.
4. Open `pipeline.py` and explain leakage-safe feature processing.
5. Show the model comparison and confusion matrix.
6. Run the Streamlit app and score a critical outage.
7. Show the probability distribution and feature contributions.
8. Open `/docs` for the FastAPI contract.
9. Show the tests and GitHub Actions workflow.
10. Finish with the model card and production-hardening roadmap.

## Strong closing line

I designed the model as one controlled component in an IT service-management process, not as an isolated notebook. The technical result matters, but the larger value is that the solution is reproducible, explainable, testable, deployable, monitorable, and safe to challenge.
