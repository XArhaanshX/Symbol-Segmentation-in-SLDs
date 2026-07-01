# Discriminative Signal Comparison

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
Compare all measured signals (Raw Chamfer, Raw Coverage, Normalization Experiments, and Structural Metrics) using discriminative metrics without declaring a winning detector.

## 2. Comparison (True Symbols vs All False Positives)
| Signal / Feature | Cohen's d | ROC-AUC | Overlap % | Pct Separation |
| :--- | :---: | :---: | :---: | :---: |
| Coverage x Area | 2.4800 | 0.9798 | 21.50% | 5.39% |
| Coverage x Scale | 1.8799 | 0.9416 | 34.72% | -7.71% |
| Coverage x sqrt(EdgeCount) | 1.0841 | 0.8001 | 58.78% | -13.66% |
| Edge Density Diff | 0.6703 | 0.6369 | 73.75% | -47.42% |
| Contour Area Error | -0.1333 | 0.4469 | 94.69% | -94.61% |
| Euler Number Diff | -0.3563 | 0.4114 | 85.86% | -100.00% |
| Contour Count Diff | -0.5090 | 0.3794 | 79.91% | -92.31% |
| Connected Comp Diff | -0.4985 | 0.3723 | 80.32% | -91.67% |
| Coverage x Scale x Density | -0.6363 | 0.3043 | 75.04% | -32.78% |
| Aspect Ratio Diff | -0.7410 | 0.2158 | 71.10% | -100.00% |
| Bounding Box IoU | -1.1198 | 0.1876 | 57.55% | -27.91% |
| Raw Coverage | -3.2153 | 0.0343 | 10.79% | -35.47% |
| Coverage / Chamfer | -4.6795 | 0.0171 | 1.93% | -73.49% |
| Raw Chamfer | -3.8897 | 0.0120 | 5.18% | -60.31% |
| Coverage x Density | -4.6165 | 0.0005 | 2.10% | -64.04% |

## 3. Findings
- Evaluates which signals provide the highest ROC-AUC and Cohen's $d$.
- Assesses whether any structural or normalized signal substantially outperforms Raw Coverage and Raw Chamfer.
