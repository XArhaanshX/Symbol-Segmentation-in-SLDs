# Audit Dataset Traceability Report

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

## 1. Data Provenance & Sources

This report certifies the provenance of every candidate proposal in the Stage 3.5 audit dataset.

- **Group A (True Symbols)**:
  - **Source Coordinates**: `reports/ground_truth_symbols.json`
  - **Extraction Logic**: Query all candidates in `outputs/candidates/ranked_candidates.csv` whose scale is $\ge 0.25$ and whose Euclidean distance to any ground-truth centroid is $\le 25.0$ pixels. Sort by Chamfer score ascending and retain the top 100.
  - **Requested Count**: 100
  - **Actual Count Obtained**: 100
  - **Shortage/Imbalance**: None. (Plenty of candidates available near verified symbols).

- **Group B (Text Regions)**:
  - **Source Coordinates**: `reports/top_100_classifications.csv`
  - **Extraction Logic**: Filter rows where `Category == 'Text Region'`.
  - **Requested Count**: 100
  - **Actual Count Obtained**: 51
  - **Shortage/Imbalance**: Shortage of 49 candidates. Because only 100 candidates were classified in the Stage 3 failure audit, the maximum available text region false positives is 51. No new heuristics were used to infer more text candidates to prevent audit contamination.

- **Group C (Conductor-related)**:
  - **Source Coordinates**: `reports/top_100_classifications.csv`
  - **Extraction Logic**: Filter rows where `Category` is either `'Conductor Intersection'` or `'Curved Conductor'`.
  - **Requested Count**: 100
  - **Actual Count Obtained**: 49
  - **Shortage/Imbalance**: Shortage of 51 candidates. Similar to Group B, Group C is bounded by the manually audited classifications from Stage 3 to preserve strict traceability.

## 2. Integrity and Anti-Contamination Controls
- **No Inferred Classifications**: We did not run connected components or scale heuristics to find more false positives from the raw candidate pool.
- **Strict Bounding**: Every candidate in the audit is traceable by its unique `sld_name, x, y, scale, rotation, score` to the original Stage 3 candidate files.
