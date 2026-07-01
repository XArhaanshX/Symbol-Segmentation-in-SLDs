# Coverage vs. Chamfer Score Relationship

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

## 1. Joint Distribution Plot

The following scatter plot maps the candidates along two dimensions: Chamfer Score (X-axis, lower is better) and Edge Coverage Ratio at 1px tolerance (Y-axis, higher is better).

![Chamfer vs Coverage Scatter Plot](C:/Users/arhaa/.gemini/antigravity/brain/773f5f67-cde3-4d67-b06f-a2fa3d7b3335/coverage_vs_chamfer.png)

---

## 2. Quantitative Correlation Analysis

We calculated the Pearson and Spearman rank correlation coefficients between Chamfer Score and Coverage Ratio (1px) for each candidate category.

| Category | Pearson Correlation ($r$) | Spearman Rank Correlation ($\rho$) | Interpretation |
| :--- | :---: | :---: | :--- |
| **True Symbols** | -0.8994 | -0.8224 | Extremely strong negative correlation. Coverage is mathematically tied to the average Chamfer distance. |
| **Text Regions** | -0.5152 | -0.4910 | Strong negative correlation. |
| **Conductors** | -0.4497 | -0.4743 | Moderate-to-strong negative correlation. |

---

## 3. Key Findings

### Do True Symbols Occupy a Distinct Region?
Yes, but they overlap with false positives. True Symbols occupy a region characterized by:
- **Chamfer Scores**: $0.54$ to $1.28$ pixels (mean $1.09$).
- **Coverage Ratio (1px)**: $0.58$ to $0.97$ (median $72.94\%$).
They exhibit a broad spread because template discretization and stroke thickness differences degrade both average distance (Chamfer score) and exact pixel matches (Coverage ratio).

### Do Text Candidates Occupy a Distinct Region?
Yes. Text candidates occupy the **bottom-left** (in terms of Chamfer score, i.e. better) and **top-left** (in terms of coverage, i.e. better) quadrant:
- **Chamfer Scores**: Extremely low ($0.48$ to $0.58$ pixels).
- **Coverage Ratio**: Extremely high ($0.87$ to $0.97$, median $93.41\%$).
This indicates that because of their small scale (scale 0.15), they are evaluated in small local windows with high edge density, which mathematically forces a very low average Chamfer distance and an extremely high coverage ratio.

### Do Conductor Candidates Occupy a Distinct Region?
Conductor candidates occupy a similar region to text candidates:
- **Chamfer Scores**: Low ($0.48$ to $0.57$ pixels).
- **Coverage Ratio**: Extremely high ($0.90$ to $0.99$, median $94.29\%$).
They align with straight busbars or circular windings in the diagram, which ensures that almost every template edge pixel falls within 1px of a diagram edge.

### Can Coverage Rescue Poor Chamfer Rankings?
**No, not via absolute thresholding.** Because the false positives (Text and Conductors) actually have *higher* coverage ratios (median $93\%$-$94\%$) than True Symbols (median $73\%$) due to scale bias and mathematical coupling, any absolute coverage filter (e.g. thresholding coverage $\ge 80\%$) would suppress the true symbols while keeping the false positives. Rather than rescuing Chamfer matching, absolute coverage filtering suffers from the exact same scale-dependent failure modes.
