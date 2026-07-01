# Structural Signal Audit

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
Determine whether structural information contains stronger discrimination than Chamfer and Coverage by measuring similarity metrics between candidate diagram crops and their corresponding templates.

## 2. Methodology
For every audited candidate:
1. **Template Features**: Extracted from the binary template edge map.
2. **Crop Features**: Extracted from the exact candidate bounding box inside the SLD edge map.
3. **Similarity Metrics**: 
   - Connected component count difference
   - Contour count difference
   - Contour area error ratio
   - Bounding box similarity (IoU)
   - Aspect ratio difference
   - Edge density difference
   - Euler number (topology consistency) difference

All metrics have been directly measured and saved to `reports/structural_metrics_dataset.csv`.
