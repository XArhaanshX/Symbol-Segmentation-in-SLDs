# Structural Dominance Assessment

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
Evaluate whether structural descriptors demonstrate substantially stronger separation than Coverage-derived signals, pursuant to the **Structural Dominance Rule**.

## 2. Finding
- **Baseline Coverage ROC-AUC**: 0.0343
- **Best Structural ROC-AUC**: 0.6369 (Edge Density Diff)

> [!NOTE]
> No single structural feature demonstrated overwhelming dominance or immediate readiness to fully replace the pipeline, though they may still provide orthogonal benefits.