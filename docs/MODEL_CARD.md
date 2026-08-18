# Model Card: IT Service Desk Priority Classifier

## Model details

| Field | Value |
|---|---|
| Model name | AI IT Service Desk Priority Predictor |
| Version | 1.0.0 |
| Model family | Multinomial logistic regression |
| Text representation | TF-IDF unigrams and bigrams |
| Additional features | One-hot categorical and scaled numerical metadata |
| Output | P1, P2, P3, or P4 probabilities and proposed class |
| Training data | 30,000 clean synthetic tickets |
| License | MIT |
| Owner | Norbert Komaromi |

## Intended use

The model is intended as a portfolio demonstration and as a prototype decision-support component for IT service desk triage. It can propose a priority and show why selected input features pushed the model toward that prediction.

The appropriate operational use is analyst assistance, workflow ordering, or shadow-mode evaluation. P1 decisions and low-confidence predictions should be confirmed by a human analyst.

## Out-of-scope use

The model must not be treated as a production-ready authority for:

- emergency, life-safety, or physical-security incident decisions;
- disciplinary or employee-performance decisions;
- fully autonomous incident escalation without governance;
- organizations whose priority definitions differ from the synthetic labeling logic;
- languages, sites, services, or ticket channels not validated with representative data.

## Data

The generator creates fictional tickets containing:

- issue description;
- category and channel;
- service criticality and site;
- affected-user count;
- VIP, outage, security, and business-hours indicators;
- related incidents during the previous 30 days;
- target priority.

It intentionally adds missing values, duplicates, typographical noise, ambiguous impact language, and class imbalance. No personal or company data is present.

### Final class distribution

| Priority | Approximate share |
|---|---:|
| P1 | 4.2% |
| P2 | 14.3% |
| P3 | 40.5% |
| P4 | 41.0% |

## Evaluation

The holdout set contains 6,000 tickets and was not used to fit TF-IDF, encoders, scalers, or model coefficients.

| Metric | Result |
|---|---:|
| Accuracy | 85.53% |
| Macro F1 | 83.16% |
| Weighted F1 | 85.63% |
| P1 precision | 70.90% |
| P1 recall | 90.87% |
| P1 F1 | 79.65% |
| P2 F1 | 78.73% |
| P3 F1 | 84.15% |
| P4 F1 | 90.12% |

### Confusion matrix

| Actual \ Predicted | P1 | P2 | P3 | P4 |
|---|---:|---:|---:|---:|
| P1 | 229 | 23 | 0 | 0 |
| P2 | 83 | 709 | 62 | 4 |
| P3 | 10 | 211 | 2,010 | 199 |
| P4 | 1 | 0 | 275 | 2,184 |

## Selection rationale

Linear SVM produced a marginally higher macro F1-score, but logistic regression was selected because it provided higher P1 recall, native probability output, lower explanation complexity, and straightforward confidence routing. The class weights intentionally place greater cost on missing P1 incidents.

## Decision policy

The model output is not the entire operational decision. The API applies the following policy:

- all proposed P1 tickets require analyst review;
- predictions with maximum probability below 0.65 require analyst review;
- the response includes the probability distribution and top positive contributions;
- the ITSM record remains the source of truth.

## Limitations

1. **Synthetic-domain gap:** generated text cannot capture the full vocabulary and ambiguity of genuine tickets.
2. **Label quality:** real priority labels may reflect inconsistent analyst behavior or local policy rather than objective severity.
3. **Calibration:** class probabilities have not yet been calibrated against real operational outcomes.
4. **Language coverage:** the model is demonstrated in English only.
5. **Concept drift:** services, products, incident types, and organizational priorities change over time.
6. **Explainability:** coefficient contributions describe model mechanics, not causality.
7. **False escalation:** improving P1 recall lowers P1 precision and may increase alert fatigue.

## Ethical and operational considerations

A model error can change response order and resource allocation. The organization should measure performance by site, channel, language, category, and business service, not only globally. Analysts must be able to override predictions and provide feedback. Prediction logs must avoid exposing ticket content beyond the approved retention and access model.

## Monitoring recommendations

- P1 precision, recall, and false-negative count;
- analyst override rate and reason;
- probability calibration;
- input and prediction drift;
- service latency and availability;
- data-quality and schema violations;
- performance segmented by business service and site.

## Retraining criteria

Retraining should be considered when:

- P1 recall falls below the accepted threshold on a sufficient labeled sample;
- override rate rises materially;
- new services or categories are introduced;
- material vocabulary or feature drift is detected;
- the priority policy changes;
- scheduled review identifies newer representative data.
