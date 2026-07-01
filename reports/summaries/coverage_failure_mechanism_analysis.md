# Coverage Failure-Mechanism Analysis

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

## 1. Analysis of False Positive Failure Mechanisms

This report investigates why certain non-symbol geometric structures achieve extremely low Chamfer scores (ranking them at the top of the Stage 3 pool) and evaluates whether Coverage Filtering addresses these failure modes.

### Failure Mechanism 1: Text Regions (e.g. "MR", "13.8kV", "50MVA" labels)
- **Why it obtains a low Chamfer score**: Letters and numbers at small scales ($0.150$ - $0.178$) consist of strokes that match individual components of the MR symbol template. Because the template is small, it contains very few edge pixels (91-115 pixels). The average Chamfer distance calculation is highly sensitive to a small number of near-zero distances.
- **Geometric match characteristics**: High local stroke density matches the bounding box corners.
- **Does coverage reduce this effect?**: **No**. Because text regions have high stroke density and the templates matching them are very small, the template edges are almost entirely covered by diagram strokes, yielding an extremely high coverage ratio (median 93.41%). 

### Failure Mechanism 2: Conductor Intersections (T-junctions, Busbars, Elbows)
- **Why it obtains a low Chamfer score**: Straight line crossings match the horizontal and vertical structures of the MR symbol. A small template placed on a long busbar can align its straight edges perfectly, resulting in 0-pixel distance for those segments.
- **Geometric match characteristics**: Alignment with infinite straight lines.
- **Does coverage reduce this effect?**: **No**. Since templates matching conductors are small (scale 0.15-0.18) and align with continuous straight busbars or circular windings, almost all template edge pixels are within 1px of diagram edges, resulting in a median coverage ratio of 94.29%.

---

## 2. Statistical Comparison of Coverage at 1px Tolerance

- **True Symbols (Group A)**: Median Coverage = **72.94%**, Mean = **74.34%**, Std Dev = **8.43%**
- **Text Regions (Group B)**: Median Coverage = **93.41%**, Mean = **94.05%**, Std Dev = **2.36%**
- **Conductors (Group C)**: Median Coverage = **94.29%**, Mean = **94.37%**, Std Dev = **2.24%**

### Visual Observations
- For **Text Regions**, edge pixels are highly matched to dense strokes, leading to large areas of green (covered) pixels and very few red (missed) pixels.
- For **Conductor Intersections**, the straight segments and windings are green (covered), resulting in almost complete coverage.
- For **True Symbols**, shape mismatches, stroke thickness variations, and discrete template discretization lead to a significant number of red (missed) pixels, lowering their coverage ratio.
