# Coverage Discriminative Power Assessment

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

## 1. Assessment of Key Questions

### Question 1: Can coverage separate True Symbols vs. Text Regions?
**No, not using an absolute minimum coverage threshold.** 
At $1$ px tolerance, the Cohen's $d$ is **-2.80** and the ROC-AUC is **0.0357**. While the separation is statistically strong, it is in the *opposite* direction of what was assumed: True Symbols have a median coverage of **72.9%**, whereas Text Regions have a higher median coverage of **93.4%**. Applying an absolute minimum coverage threshold will eliminate the true symbols while retaining the text regions. Separation is only possible if we apply a maximum coverage threshold or a scale-normalized metric.

### Question 2: Can coverage separate True Symbols vs. Conductors?
**No, not using an absolute minimum coverage threshold.**
At $1$ px tolerance, the Cohen's $d$ is **-2.83** and the ROC-AUC is **0.0329**. Similar to text regions, conductors have a higher median coverage (**94.3%**) than True Symbols (**72.9%**). Therefore, absolute coverage filtering cannot separate true symbols from conductors.

### Question 3: Which tolerance radius provides the greatest separation?
The **1 pixel tolerance radius** provides the greatest overall separation:
- True vs. Text Cohen's $d$: **-2.80** (compared to -3.46 at 0px and -2.87 at 2px).
- True vs. Conductor Cohen's $d$: **-2.83** (compared to -3.40 at 0px and -2.77 at 2px).
- At 0px tolerance, the metrics are highly sensitive to 1-pixel digitization offsets, degrading the true symbol coverage. At 2px and 3px, the tolerance is too loose, allowing text and conductor false positives to inflate their coverage by matching distant edges, reducing the separation gap.

### Question 4: Does coverage provide information not already captured by Chamfer score?
**No.**
As shown in the joint relationship analysis, Chamfer score and coverage ratio are extremely strongly negatively correlated ($r \approx -0.90$). Because coverage ratio is a monotonic function of the Chamfer score, it does not provide independent geometric information. The high coverage of false positives is directly coupled to their extremely low Chamfer scores.

### Question 5: Would coverage likely improve ranking quality?
**No.**
Because false positives have higher coverage ratios than true symbols, a simple coverage-based filter or re-ranking will actually *worsen* the ranking quality by preferring false positives over true symbols. To improve ranking, we must use features that are orthogonal to Chamfer score, such as Stage 5 PCA structural verification or scale-normalized score calibration.
