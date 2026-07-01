# Audit Candidate Dataset Summary

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

## 1. Dataset Breakdown

This report summarizes the balanced audit dataset constructed to evaluate the discriminative power of Coverage Filtering. Candidates are divided into three groups based on manual classifications from Stage 3.

| Group | Category | Count | Origin File | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Group A** | True Symbol | 100 | `reports/ground_truth_symbols.json` | Top-ranked candidates overlapping with verified symbol locations. |
| **Group B** | Text Region | 51 | `reports/top_100_classifications.csv` | Top-ranked false positives consisting of annotations/labels. |
| **Group C** | Conductor | 49 | `reports/top_100_classifications.csv` | Top-ranked false positives consisting of lines/windings. |

---

## 2. Candidate List (First 10 of each Category)

### Group A: True Symbols
| Candidate ID | SLD | Coord (X, Y) | Scale | Rotation | Chamfer Score |
| :---: | :--- | :---: | :---: | :---: | :---: |
| A_001 | SLD4 | (428,129) | 0.261 | 0° | 0.5436 |
| A_002 | SLD4 | (569,128) | 0.261 | 0° | 0.5493 |
| A_003 | SLD3 | (480,170) | 0.261 | 0° | 0.5887 |
| A_004 | SLD3 | (1378,170) | 0.261 | 0° | 0.5934 |
| A_005 | SLD3 | (194,168) | 0.261 | 0° | 0.6741 |
| A_006 | SLD11 | (515,309) | 0.261 | 270° | 0.7079 |
| A_007 | SLD1 | (576,102) | 0.400 | 180° | 0.7096 |
| A_008 | SLD3 | (1092,170) | 0.261 | 0° | 0.7211 |
| A_009 | SLD4 | (568,126) | 0.289 | 0° | 0.7405 |
| A_010 | SLD11 | (512,304) | 0.289 | 270° | 0.7435 |

### Group B: Text Regions
| Candidate ID | SLD | Coord (X, Y) | Scale | Rotation | Chamfer Score |
| :---: | :--- | :---: | :---: | :---: | :---: |
| B_001 | SLD11 | (634,79) | 0.150 | 90° | 0.4879 |
| B_002 | SLD8 | (421,138) | 0.206 | 180° | 0.4993 |
| B_003 | SLD8 | (430,142) | 0.150 | 180° | 0.5042 |
| B_004 | SLD7 | (543,227) | 0.150 | 90° | 0.5055 |
| B_005 | SLD2 | (108,58) | 0.150 | 90° | 0.5099 |
| B_006 | SLD2 | (542,58) | 0.150 | 90° | 0.5143 |
| B_007 | SLD2 | (542,405) | 0.150 | 90° | 0.5165 |
| B_008 | SLD7 | (543,244) | 0.150 | 90° | 0.5187 |
| B_009 | SLD7 | (315,94) | 0.150 | 180° | 0.5188 |
| B_010 | SLD11 | (488,79) | 0.150 | 90° | 0.5253 |

### Group C: Conductor-related
| Candidate ID | SLD | Coord (X, Y) | Scale | Rotation | Chamfer Score |
| :---: | :--- | :---: | :---: | :---: | :---: |
| C_001 | SLD7 | (441,85) | 0.178 | 0° | 0.4869 |
| C_002 | SLD2 | (335,427) | 0.150 | 0° | 0.5000 |
| C_003 | SLD7 | (1061,502) | 0.178 | 0° | 0.5113 |
| C_004 | SLD7 | (442,502) | 0.178 | 0° | 0.5130 |
| C_005 | SLD10 | (279,119) | 0.178 | 0° | 0.5130 |
| C_006 | SLD9 | (867,146) | 0.150 | 90° | 0.5187 |
| C_007 | SLD1 | (1021,42) | 0.150 | 0° | 0.5216 |
| C_008 | SLD2 | (790,427) | 0.150 | 0° | 0.5235 |
| C_009 | SLD7 | (442,504) | 0.150 | 0° | 0.5294 |
| C_010 | SLD10 | (279,648) | 0.178 | 0° | 0.5304 |

*[Refer to reports/audit_candidate_dataset.csv for the complete list]*
