# Stage 4 Rescoring Methodology

<!-- Traceability Header -->
- **Generation Timestamp**: 2026-06-17 02:11:33
- **Template Bank Version**: Stage2_D3_v1
- **Stage 3 Candidate Source**: outputs/candidates/ranked_candidates.csv
- **Coverage Method Source**: Stage 3.5
- **Normalization Method Source**: Stage 3.6
- **Manifest Version**: outputs/template_bank/template_bank_manifest.csv
- **Candidate Count Before Rescoring**: 264852
- **Candidate Count After Rescoring**: 264852
- **SLD Count**: 10
- **Investigation Type**: Operational Rescoring
<!-- End Traceability Header -->



## 1. Methodology
For every candidate across all SLDs, Stage 4 recomputed coverage against the distance transform using exact Stage 3.5 methodology:
$Coverage\_R = \frac{\text{edge pixels within } R}{\text{total template edges}}$

Following recomputation, diagnostic models from Stage 3.6 were applied to synthesize operationally normalized scores:
- `NormalizedScore_A` = $Coverage\_R1 \\times Scale$
- `NormalizedScore_B` = $Coverage\_R1 \\times TemplateArea$
- `NormalizedScore_C` = Coverage_R1 \times Scale \times EdgeDensity

## 2. Pipeline Integrity
The ground truth evaluation and rank analysis are completely separated from this operational engine. All ranked CSVs are preserved in `outputs/candidates/`.
