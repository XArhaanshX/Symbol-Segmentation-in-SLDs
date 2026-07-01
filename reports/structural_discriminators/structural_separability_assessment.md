# Structural Separability Assessment

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
Quantify the discriminative power of structural descriptors comparing True Symbols against Text Regions and Conductors.

## 2. True Symbols vs Text Regions
| Metric | Cohen's d | ROC-AUC | Overlap % | Pct Separation |
| :--- | :---: | :---: | :---: | :---: |
| Connected Comp Diff | -0.0513 | 0.5011 | 97.96% | -75.00% |
| Contour Count Diff | -0.0878 | 0.4991 | 96.50% | -80.77% |
| Contour Area Error | -0.0071 | 0.4994 | 99.72% | -94.37% |
| Bounding Box IoU | -1.1036 | 0.1724 | 58.11% | -27.91% |
| Aspect Ratio Diff | -0.8359 | 0.1686 | 67.60% | -100.00% |
| Edge Density Diff | 1.6390 | 0.8459 | 41.25% | -38.61% |
| Euler Number Diff | -0.1211 | 0.4825 | 95.17% | -91.67% |

## 3. True Symbols vs Conductors
| Metric | Cohen's d | ROC-AUC | Overlap % | Pct Separation |
| :--- | :---: | :---: | :---: | :---: |
| Connected Comp Diff | -0.9712 | 0.2383 | 62.73% | -91.67% |
| Contour Count Diff | -0.9257 | 0.2548 | 64.35% | -92.31% |
| Contour Area Error | -0.2617 | 0.3922 | 89.59% | -94.57% |
| Bounding Box IoU | -0.9793 | 0.2035 | 62.44% | -27.91% |
| Aspect Ratio Diff | -0.5153 | 0.2649 | 79.67% | -100.00% |
| Edge Density Diff | -0.1450 | 0.4194 | 94.22% | -78.17% |
| Euler Number Diff | -0.5769 | 0.3374 | 77.30% | -100.00% |
