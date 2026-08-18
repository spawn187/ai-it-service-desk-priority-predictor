# Comprehensive AI/ML Technical Report

## Project title

**AI-Powered IT Service Desk Ticket Classification and Priority Prediction System**

## Executive summary

This project implements an end-to-end machine learning workflow for prioritizing IT service desk tickets from P1 to P4. The prototype combines natural-language processing of ticket descriptions with structured operational metadata including service criticality, affected-user count, category, site, channel, and outage or security indicators. The business objective is to reduce inconsistent manual triage while protecting the organization against missed critical incidents.

A deterministic generator creates 30,000 synthetic tickets and intentionally adds duplicates, missing values, typographical noise, ambiguous language, and class imbalance. The selected model uses TF-IDF unigrams and bigrams, one-hot categorical features, imputed and scaled numerical values, and cost-sensitive logistic regression. On a 6,000-record holdout set it achieved 85.53% accuracy, 83.16% macro F1, and 90.87% recall for P1 incidents.

## 1. Problem analysis

Manual ticket prioritization is operationally important because response targets and escalation paths depend on impact and urgency. Missing a genuine P1 can delay specialist engagement and extend business disruption. Over-classifying routine requests as P1 creates alert fatigue and consumes scarce engineering capacity. The prototype therefore treats P1 recall as a primary safety metric while also tracking P1 precision, aggregate F1 scores, and the full confusion matrix.

The intended operating model is decision support rather than autonomous incident management. Every proposed P1 and every prediction below 65% confidence requires analyst confirmation. The ITSM platform remains the system of record.

## 2. Dataset

The public repository uses synthetic data so it contains no real company, customer, employee, host, or incident information. Each ticket includes a free-text description, category, channel, service criticality, site, affected-user count, VIP indicator, outage indicator, security indicator, business-hours indicator, recent related-incident count, and target priority.

The final class distribution is intentionally imbalanced: approximately 4.2% P1, 14.3% P2, 40.5% P3, and 41.0% P4. The generator also introduces missing values, duplicates, typographical errors, and ambiguous impact phrases to make the workflow demonstrate realistic validation and preprocessing concerns.

## 3. Technique selection

The task is supervised multi-class classification. Ticket text is represented with TF-IDF using unigrams and bigrams, while categorical features are one-hot encoded and numerical features are median-imputed and scaled. All preprocessing is contained in a single scikit-learn `Pipeline` and `ColumnTransformer`, ensuring that transformations are fit only on training data.

Three candidate models were compared: logistic regression, linear SVM, and SGD classification with log loss. Logistic regression was selected because it combined high P1 recall with native probability output, low inference cost, and straightforward coefficient-based explanations. Linear SVM achieved slightly higher macro F1, but its lower P1 recall and lack of native probabilities made it less suitable for the confidence-based routing policy used by the prototype.

## 4. Implementation

The reusable package lives under `src/it_ticket_priority`. Data generation, validation, feature engineering, training, evaluation, experiment tracking, schemas, and inference are separated into modules. Command-line scripts reproduce generation, training, evaluation, and prediction. FastAPI exposes health, model metadata, and prediction endpoints. Streamlit provides an interview-friendly interactive interface.

GitHub Actions installs the project, runs Ruff, executes automated tests with coverage, and performs a lightweight training smoke test. Docker and Docker Compose provide containerized API and dashboard execution. MLflow support is optional through environment variables; when MLflow is not configured, experiment metadata is stored as local JSON.

## 5. Evaluation

| Model | Accuracy | Macro F1 | P1 precision | P1 recall |
|---|---:|---:|---:|---:|
| Logistic regression | 85.53% | 83.16% | 70.90% | 90.87% |
| SGD log loss | 84.30% | 81.36% | 69.30% | 90.48% |
| Linear SVM | 85.32% | 83.60% | 75.85% | 88.49% |

The selected logistic-regression model correctly identified 229 of 252 P1 tickets. Twenty-three P1 incidents were predicted as P2 and none as P3 or P4. P1 precision is intentionally lower than recall because the class weighting prefers human review over a missed critical incident.

The most important limitation is the synthetic-domain gap. These metrics demonstrate that the engineering pipeline is reproducible and internally consistent; they do not establish performance on a real organization’s ticket distribution. Production validation would require approved anonymized historical data, label auditing, temporal testing, calibration, and segmented evaluation.

## 6. Deployment and monitoring

A real rollout should begin in shadow mode. The model would score incoming tickets without changing workflow while analysts continue assigning priority. Disagreements would be reviewed to assess label quality, calibration, and business-policy alignment.

Operational monitoring should include API availability, latency, errors, schema violations, feature missingness, vocabulary and feature drift, priority distribution, confidence, analyst overrides, and delayed labeled metrics. P1 recall and P1 false-negative count are the primary safety indicators. Drift should trigger investigation and controlled retraining rather than automatic replacement of an approved model.

## 7. Security and governance

Real service desk text can contain personal information, hostnames, IP addresses, screenshots, access details, and security-sensitive content. A production implementation therefore requires authentication, authorization, encryption, least-privilege access, secret management, PII redaction, audit logging, retention controls, dependency and image scanning, and a documented rollback path. The prediction service must never block ticket creation when unavailable; manual triage remains the fallback.

## 8. Conclusion

The project demonstrates a complete machine learning engineering approach to IT service desk prioritization: reproducible data generation, data-quality controls, leakage-safe preprocessing, model comparison, business-oriented evaluation, explainable inference, API delivery, interactive demonstration, automated testing, CI, containerization, experiment tracking, documentation, and a production-hardening plan.

The technical result matters, but the strongest portfolio value is that the model is treated as one controlled component inside an accountable IT service-management process rather than as an isolated notebook.

## References

1. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
2. Salton, G., & Buckley, C. (1988). *Term-weighting approaches in automatic text retrieval*. Information Processing & Management, 24(5), 513-523.
3. Breck, E., et al. (2017). *The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction*. IEEE Big Data.
