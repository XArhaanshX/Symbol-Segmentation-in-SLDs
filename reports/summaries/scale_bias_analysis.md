# Root Cause Quantification & Scale Bias Analysis

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
Determine why Coverage Filtering failed and whether small-scale bias is the primary root cause.

## 2. Visual Evidence
![Coverage vs Scale](scale_bias_coverage_vs_scale.png)
![Chamfer vs Scale](scale_bias_chamfer_vs_scale.png)
![Rank vs Scale](scale_bias_rank_vs_scale.png)
![Edge Count vs Scale](scale_bias_edge_count_vs_scale.png)

## 3. Scale Bias Quantification
The measured evidence confirms a severe **Scale Bias**:
- **False Positives (Text & Conductors)**: Strongly clustered at low scales (e.g. 0.150 - 0.178). At these scales, the template edge count is small (approx 90-140 pixels). When evaluated in dense diagram regions, these small templates trivially find edge support, leading to near-perfect Coverage (> 90%) and exceptionally low Chamfer distances.
- **True Symbols**: Distributed across larger scales (0.250 - 0.400). Larger templates encompass far more area and have higher edge counts, rendering them much more susceptible to stroke width mismatches, occlusions, and discrete pixel quantization. As scale increases, the achievable Chamfer score degrades, and Coverage drops.
- **Root Cause**: Coverage is functionally dependent on the template scale/area. Small templates inevitably secure higher coverage ratios than large templates in complex diagram regions.
