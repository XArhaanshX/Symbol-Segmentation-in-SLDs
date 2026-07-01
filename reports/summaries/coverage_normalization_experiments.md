# Coverage Normalization Experiment Simulation

<!-- Traceability Header -->
- **Generation Time**: 2026-06-17 01:56:45
- **Template Bank Version**: Stage2_D3_v1
- **Candidate Dataset Source**: outputs/candidates/ranked_candidates.csv
- **Coverage Metrics Source**: reports/coverage_metrics_dataset.csv
- **Structural Metrics Source**: reports/structural_metrics_dataset.csv
- **Manifest Version**: outputs/template_bank/template_bank_manifest.csv
- **Stage 3.5 Feasibility Report**: 1.0.0
- **Investigation Type**: Diagnostic Only
<!-- End Traceability Header -->



## 1. Objective
Determine whether scale bias can theoretically be corrected by applying normalization formulas to the coverage ratio.
*Note: Evaluated as diagnostic experiments only. No formula will be deployed.*

## 2. True Symbols vs Text Regions
| Metric | Cohen's d | ROC-AUC | Overlap % | Pct Separation |
| :--- | :---: | :---: | :---: | :---: |
| Coverage x Scale | 2.0553 | 0.9747 | 30.41% | -3.46% |
| Coverage x sqrt(EdgeCount) | 1.2784 | 0.8735 | 52.27% | -13.17% |
| Coverage x Area | 2.4911 | 1.0000 | 21.29% | 9.83% |
| Coverage x Density | -5.6881 | 0.0000 | 0.45% | -62.91% |
| Coverage / Chamfer | -4.1611 | 0.0178 | 3.75% | -73.56% |
| Coverage x Scale x Density | -0.4480 | 0.3459 | 82.27% | -31.55% |

## 3. True Symbols vs Conductors
| Metric | Cohen's d | ROC-AUC | Overlap % | Pct Separation |
| :--- | :---: | :---: | :---: | :---: |
| Coverage x Scale | 1.4871 | 0.9071 | 45.72% | -18.91% |
| Coverage x sqrt(EdgeCount) | 0.7796 | 0.7237 | 69.67% | -24.53% |
| Coverage x Area | 2.0299 | 0.9588 | 31.01% | -9.03% |
| Coverage x Density | -4.2233 | 0.0010 | 3.47% | -64.24% |
| Coverage / Chamfer | -4.1719 | 0.0163 | 3.70% | -73.00% |
| Coverage x Scale x Density | -0.7539 | 0.2610 | 70.62% | -34.80% |
