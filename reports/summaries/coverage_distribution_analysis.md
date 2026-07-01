# Coverage Distribution Analysis

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

## 1. Coverage Statistics by Category and Tolerance

We measured the template edge coverage ratios across three categories at 0px, 1px, 2px, and 3px tolerances.

### Tolerance = 0 pixels
| Category | Min | Max | Mean | Median | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **True Symbols** | 0.2500 | 0.5032 | 0.3387 | 0.3299 | 0.0531 |
| **Text Regions** | 0.4479 | 0.5417 | 0.4968 | 0.5055 | 0.0243 |
| **Conductors** | 0.4444 | 0.5652 | 0.4960 | 0.4957 | 0.0257 |

### Tolerance = 1 pixel
| Category | Min | Max | Mean | Median | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **True Symbols** | 0.5862 | 0.9718 | 0.7434 | 0.7294 | 0.0843 |
| **Text Regions** | 0.8791 | 0.9784 | 0.9405 | 0.9341 | 0.0236 |
| **Conductors** | 0.9043 | 0.9902 | 0.9437 | 0.9429 | 0.0224 |

### Tolerance = 2 pixels
| Category | Min | Max | Mean | Median | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **True Symbols** | 0.7877 | 1.0000 | 0.8690 | 0.8552 | 0.0530 |
| **Text Regions** | 0.9739 | 1.0000 | 0.9943 | 1.0000 | 0.0066 |
| **Conductors** | 0.9739 | 1.0000 | 0.9909 | 0.9902 | 0.0089 |

### Tolerance = 3 pixels
| Category | Min | Max | Mean | Median | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **True Symbols** | 0.8621 | 1.0000 | 0.9379 | 0.9337 | 0.0310 |
| **Text Regions** | 0.9929 | 1.0000 | 0.9999 | 1.0000 | 0.0010 |
| **Conductors** | 0.9857 | 1.0000 | 0.9994 | 1.0000 | 0.0026 |

---

## 2. Coverage Histograms & Density Curves

![Coverage Distribution Plot](C:/Users/arhaa/.gemini/antigravity/brain/773f5f67-cde3-4d67-b06f-a2fa3d7b3335/coverage_distributions.png)

> [!NOTE]
> The distributions reveal that at 1px tolerance, false positives (Text Regions and Conductors) actually exhibit higher coverage (mean $\approx 94.1%$ and $94.4%$) than True Symbols (mean $\approx 74.3%$). This is due to the small-scale bias of top-ranked false positives and shape mismatches of larger true symbols. Detailed separability analysis is conducted in `reports/coverage_separability_analysis.md`.
