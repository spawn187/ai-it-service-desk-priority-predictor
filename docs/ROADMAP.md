# Roadmap

## Completed: portfolio-grade baseline

- [x] Reproducible 30,000-row synthetic dataset generator
- [x] Missing-value, duplicate, and schema handling
- [x] TF-IDF plus categorical and numerical feature pipeline
- [x] Logistic regression, linear SVM, and SGD comparison
- [x] Stratified cross-validation and holdout evaluation
- [x] P1-focused class weighting
- [x] Model artifact and metadata persistence
- [x] FastAPI prediction service
- [x] Streamlit interactive demo
- [x] Local feature-contribution explanation
- [x] Docker and Docker Compose
- [x] Automated tests and GitHub Actions
- [x] Optional MLflow tracking
- [x] Model card, architecture, technical report, and interview guide

## Next: production-oriented improvements

- [ ] Calibrate class probabilities using a validation split
- [ ] Learn decision thresholds from explicit incident-cost assumptions
- [ ] Add a shadow-mode event store for predictions and analyst overrides
- [ ] Add PSI/KS or embedding-based drift reports
- [ ] Add multilingual text normalization and evaluation
- [ ] Add PII/secret detection and redaction
- [ ] Add API authentication, authorization, and rate limiting
- [ ] Add model registry integration and signed artifact verification
- [ ] Add canary deployment and automatic rollback checks
- [ ] Add load and resilience testing
- [ ] Add OpenTelemetry traces and structured JSON logging

## Real-data pilot gates

A move beyond synthetic data should require all of the following:

1. approved anonymized data access and retention rules;
2. documented priority-label policy and quality audit;
3. representative train, validation, and temporal test periods;
4. performance segmented by service, site, language, and channel;
5. probability calibration and cost-sensitive threshold approval;
6. shadow-mode pilot with analyst override capture;
7. security, privacy, architecture, and change approvals;
8. rollback and manual-continuity plan.
