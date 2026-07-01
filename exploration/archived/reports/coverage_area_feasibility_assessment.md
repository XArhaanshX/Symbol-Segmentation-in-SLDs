# Stage 4 Feasibility Assessment

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

## 1. Evidence Summary

This report assesses the feasibility of implementing **Stage 4 (Coverage Filtering)** exactly as specified by the PRD, based on the empirical evidence gathered during this audit stage.

### Summary of Coverage Statistics (Tolerance = 1px)
- **True Symbols (Group A)**: Mean = **74.34%** | Median = **72.94%**
- **Text Regions (Group B)**: Mean = **94.05%** | Median = **93.41%**
- **Conductors (Group C)**: Mean = **94.37%** | Median = **94.29%**

### Observed Separation Strength
- **True Symbols vs. Text Regions**: **Inverted Separation (False Positives have higher coverage)**
  - Cohen's $d$: **-2.7991**
  - ROC-AUC: **0.0357**
  - Estimated Overlap: **16.16%**
  - Percentile Separation: **-34.69%**
- **True Symbols vs. Conductors**: **Inverted Separation (False Positives have higher coverage)**
  - Cohen's $d$: **-2.8330**
  - ROC-AUC: **0.0329**
  - Estimated Overlap: **15.66%**
  - Percentile Separation: **-34.92%**

---

## 2. Risks and Limitations of Coverage Filtering

1. **Severe Scale Bias**:
   - Small templates used for text regions (scale 0.150) and conductors (scale 0.150-0.178) occupy very small pixel windows. In areas of high local edge density, these small templates achieve extremely low Chamfer scores and near-perfect coverage ratios (median 93.41% and 94.29% respectively).
   - Larger templates matching True Symbols (scale 0.25-0.45) cover much larger windows, making them far more sensitive to stroke width variations and discretization. They achieve lower coverage ratios (median 72.94%).

2. **Mathematical Coupling and Redundancy**:
   - Coverage ratio is almost perfectly negatively correlated with Chamfer score ($r \approx -0.90$ for True Symbols).
   - It does not act as an independent discriminative feature; it is mathematically coupled to the average distance. Since Stage 3 ranked false positives higher (better Chamfer score), they automatically obtain higher coverage ratios.

---

## 3. Expected Stage 4 Benefits

- **No benefit from absolute coverage thresholding**: Implementing Stage 4 as an absolute minimum coverage filter (e.g. threshold $\ge 80\%$) would suppress **79.0%** of True Symbols while retaining **100%** of Text and Conductor false positives.
- **Alternative Implementation Strategy Required**: To yield benefits, Stage 4 must use scale-normalized scores or scale-dependent coverage thresholds, rather than the absolute global threshold specified in the PRD.

---

## 4. Outstanding Unknowns

- **Scale-Normalized Calibration**: Can we normalize the Chamfer score and coverage ratio by the template scale to eliminate small-scale bias?
- **Stage 5 Structural Validation**: Can structural verification (e.g. PCA or layout rules in Stage 5) bypass these coverage limits and robustly filter conductor crossings?

---

## 5. User Review Required

> [!WARNING]
> The empirical evidence **does not justify proceeding with absolute global Coverage Filtering** as originally specified in the PRD.
> Because false positives (Text/Conductors) are smaller and mathematically coupled to Chamfer score, they achieve higher coverage ratios than True Symbols. Absolute thresholding is mathematically and empirically invalid.
>
> **Recommendations for Stage 4**:
> 1. **Reject the PRD design** for absolute global coverage thresholding.
> 2. **Implement Scale-Normalized Chamfer/Coverage Scoring** in Stage 4 to penalize small-scale matches.
> 3. **Rely on Stage 5 PCA Verification** as the primary engine for false positive suppression.
>
> **Human Review Decision**: The engineering team recommends a redesign of Stage 4 based on these diagnostic findings before beginning implementation.
