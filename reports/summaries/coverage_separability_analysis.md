# Coverage Separability Analysis

<!-- Traceability Header -->
- **Generation Time**: 2026-06-17 01:36:48
- **Template Bank Version**: Stage2_D3_v1
- **Candidate Dataset Source**: outputs/candidates/ranked_candidates.csv
- **Measured Candidate Count**: 200 total
- **Measured Category Counts**: True Symbols: 100, Text Regions: 51, Conductor-related: 49
- **Association Radius**: 25.0 pixels
- **Coordinate Source Files**: `reports/ground_truth_symbols.json`, `reports/top_100_classifications.csv`
- **Coverage Tolerances Evaluated**: 0, 1, 2, 3 px
- **SLD Count**: 10
- **Manifest Version**: outputs/template_bank/template_bank_manifest.csv
- **Stage 3 Candidate File Version**: ranked_candidates.csv (latest build)
- **Audit Dataset Version**: 1.0.0
<!-- End Traceability Header -->

---

## 1. Separability Metrics by Tolerance Radius

We computed standardized separability metrics to evaluate the discriminative power of Coverage Filtering.

### True Symbols vs. Text Regions

| Tolerance | Cohen's $d$ | Est. Overlap | ROC-AUC | Percentile Separation |
| :---: | :---: | :---: | :---: | :---: |
| **0 px** | -3.4558 | 8.40% | 0.0092 | -26.62% |
| **1 px** | -2.7991 | 16.16% | 0.0357 | -34.69% |
| **2 px** | -2.8737 | 15.08% | 0.0241 | -20.32% |
| **3 px** | -2.4358 | 22.33% | 0.0204 | -10.18% |

### True Symbols vs. Conductors

| Tolerance | Cohen's $d$ | Est. Overlap | ROC-AUC | Percentile Separation |
| :---: | :---: | :---: | :---: | :---: |
| **0 px** | -3.4034 | 8.88% | 0.0102 | -27.41% |
| **1 px** | -2.8330 | 15.66% | 0.0329 | -34.92% |
| **2 px** | -2.7698 | 16.61% | 0.0273 | -20.32% |
| **3 px** | -2.3961 | 23.09% | 0.0227 | -10.18% |

---

## 2. Methodology & Mathematical Definitions

- **Cohen's $d$**: Standardized mean difference. A value of $d > 0.8$ represents a large effect size; $d > 2.0$ represents extremely strong separation.
- **Estimated Overlap**: The shared area under two fitted normal distributions: $2 \Phi(-|d|/2)$.
- **ROC-AUC**: The Area Under the Receiver Operating Characteristic curve. An AUC of $1.0$ represents perfect classification; $0.5$ represents random guessing.
- **Percentile Separation**: The difference between the 5th percentile of the True Symbols and the 95th percentile of the false positives. A positive value indicates a clean separation gap.
