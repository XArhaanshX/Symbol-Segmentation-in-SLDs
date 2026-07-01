# Chapter 9 — Structural Verification and Discriminator Discovery

## 9.1 Stage 5 Verification Architecture

### 9.1.1 Design Intent

With Chamfer matching providing localization (but poor ranking) and coverage rescoring providing partial rank improvement (but redundant signal), Stage 5 introduced **structural verification** — a set of topological and morphological features computed by comparing each candidate's edge patch against the matched template.

The hypothesis: if true MR symbols have distinctive structural properties (specific connected component counts, contour counts, aspect ratios, edge densities), these properties could discriminate true positives from false positives within the ranked candidate pool.

### 9.1.2 Budget Management

Computing structural features is computationally expensive (requiring per-candidate image operations). To manage cost, Stage 5 operates on a **budgeted subset**:

- **Strategy**: PER_SLD_TOP_N (top-N candidates per SLD, ranked by CoverageAreaScore)
- **Limit**: 1,000 candidates per SLD
- **Total**: ~10,000 candidates (10 SLDs × 1,000 each)

This budget was validated as sufficient because the majority of true MR symbols appear within the top 1,000 per SLD after Stage 4 rescoring (for scale regimes A and B).

## 9.2 Feature Groups

### 9.2.1 Group A — Connected Component Features

For each candidate patch, the number of connected components is computed using `cv2.connectedComponents`. The difference from the template's component count provides a structural similarity signal.

**Expected behavior**: MR symbols should have a specific component count (typically 1-3 components in the cropped patch). Text regions and conductor junctions would have different component counts.

**Measured discriminative power**: Component features showed moderate separability but high overlap between groups.

### 9.2.2 Group B — Contour Features

Contour count, total contour area, and total contour perimeter are computed via `cv2.findContours` with `RETR_CCOMP` retrieval mode (two-level hierarchy: outer contours and holes).

**Key insight**: The contour hierarchy enables computation of the **Euler number** (components - holes), which captures the topological complexity of the candidate.

### 9.2.3 Group C — Geometry Features

Aspect ratio and bounding box area measure the geometric envelope of the foreground content within the candidate patch.

### 9.2.4 Group D — Edge Density

Edge density (foreground pixels / total patch area) measures how "busy" the candidate region is. Dense text regions have high edge density; sparse background regions have low density.

### 9.2.5 Group E — Foreground Occupancy

Occupancy (foreground pixels / bounding box area) measures how efficiently the foreground fills its bounding box. MR symbols have a specific occupancy profile due to their characteristic shape.

### 9.2.6 Group F — Topology

The Euler number and hole count provide topological invariants. These are mathematically elegant discriminators but proved to be noisy at small scales due to edge fragmentation.

### 9.2.7 Group G — Similarity Metrics

- **Edge overlap ratio**: Fraction of template edges overlapping with candidate edges (pixel-level intersection)
- **Shape similarity**: `cv2.matchShapes` using Hu moments (rotation-invariant shape comparison)
- **Localized Chamfer residual**: Chamfer distance recomputed at the candidate location using the saved distance transform

## 9.3 Verification Score Computation

The individual feature similarities are combined into a single VerificationScore using configurable weights:

```python
VerificationScore = (
    0.15 × s_component +
    0.10 × s_contour +
    0.15 × s_geometry +
    0.10 × s_density +
    0.10 × s_occupancy +
    0.15 × s_topology +
    0.15 × s_similarity
)
```

The combined score blends verification with coverage:

```python
CombinedScore = 0.60 × VerificationScore + 0.40 × CoverageAreaScore
```

## 9.4 Stage 5.8: Structural Discriminator Discovery

### 9.4.1 Experimental Design

Stage 5.8 was a dedicated research investigation (`stage5_8_structural_discovery.py`) designed to systematically evaluate which structural features best separate true MR symbols from false positives.

The investigation constructed four candidate groups:

| Group | Name | Definition | Count |
|---|---|---|---|
| A | True MR | Candidates within 25px of ground truth center | ~60–80 |
| B | Dominant FP | Candidates appearing in the top-100 competitor sheet | ~100–150 |
| C | Hard Negatives | Top-10 per SLD candidates that are NOT MR and NOT dominant FP | ~60–80 |
| D | Random Background | Random sample from rank > 50 candidates | ~20–40 |

### 9.4.2 Feature Extraction: Topological Features

Beyond the basic structural features of Stage 5, the discovery script extracted **16 advanced topological features** using skeletonization, Hough line detection, and graph analysis:

1. **Connected_Component_Count**: CC count via `cv2.connectedComponentsWithStats`
2. **Largest_Component_Ratio**: Largest CC area / total foreground area
3. **Component_Area_Variance**: Variance of CC areas
4. **Loop_Count**: Number of outer contours (cv2.RETR_TREE hierarchy)
5. **Hole_Count**: Number of inner contours (children in hierarchy)
6. **Euler_Number**: Components - Holes
7. **Contour_Hierarchy_Depth**: Maximum nesting depth in contour tree
8. **Endpoint_Count**: Skeleton pixel with exactly 1 neighbor (via convolution filter)
9. **Branch_Point_Count**: Skeleton pixel with 3+ neighbors
10. **Average_Branch_Length**: Total skeleton length / (branch points + 1)
11. **Maximum_Branch_Length**: Estimated maximum branch segment
12. **Branch_Length_Variance**: Variance of branch segment lengths
13. **Stroke_Count**: Number of line segments detected by Hough line transform
14. **Stroke_Density**: Stroke count / component count
15. **Horizontal_Stroke_Ratio**: Fraction of strokes within 20° of horizontal
16. **Vertical_Stroke_Ratio**: Fraction of strokes within 20° of vertical

Additionally, **9 graph-based features** were computed using networkx:
- Node_Count_Difference, Edge_Count_Difference, Degree_Distribution_Difference
- Graph_Density_Difference, Junction_Similarity, Endpoint_Similarity
- Graph_Edit_Distance_Approx, Endpoint_Matching_Ratio, Junction_Matching_Ratio

### 9.4.3 Separability Analysis Methodology

For each feature, three separability metrics were computed across each group pair:

1. **ROC-AUC**: Area under the ROC curve for binary classification between the two groups using the feature as a single-variable classifier
2. **Cohen's d**: Standardized effect size measuring the difference between group means in units of pooled standard deviation
3. **Distribution Overlap**: Percentile overlap between the two distributions

### 9.4.4 Results: Discriminator Leaderboard

The top features ranked by AUC against Dominant FP (Group B):

| Rank | Feature | AUC (vs DomFP) | Cohen's d | Overlap |
|---|---|---|---|---|
| 1 | **Stroke_Count** | **0.951** | **2.647** | **5.2%** |
| 2 | Branch_Point_Count | 0.896 | 1.832 | 14.3% |
| 3 | Stroke_Density | 0.878 | 1.654 | 18.7% |
| 4 | Average_Branch_Length | 0.823 | 1.245 | 27.1% |
| 5 | Endpoint_Count | 0.757 | 0.923 | 35.4% |

**Stroke_Count** achieved the strongest separability with AUC=0.951 and Cohen's d=2.647, meaning the true MR and Dominant FP populations are separated by nearly 3 pooled standard deviations.

### 9.4.5 Critical Finding: Zero Separability Against Hard Negatives

While all features showed strong separability against Dominant FP and Random Background groups, they showed **AUC ≈ 0.500 (random)** against Hard Negatives (Group C):

| Feature | AUC (vs DomFP) | AUC (vs HardNeg) | AUC (vs RandBG) |
|---|---|---|---|
| Stroke_Count | 0.951 | ~0.500 | 0.923 |
| Branch_Point_Count | 0.896 | ~0.500 | 0.867 |
| All features | High | **~Random** | High |

**Interpretation**: Hard negatives — candidates ranked in the top-10 per SLD that are neither true MR symbols nor identified dominant false positives — have structural properties indistinguishable from true MR symbols. These are the candidates that survive all filtering and remain as irreducible false positives.

### 9.4.6 Redundancy Analysis

Each feature was checked for correlation with existing pipeline signals:

| Feature | Redundancy Class | Best Correlation | Correlated Signal | Shared Variance (R²) |
|---|---|---|---|---|
| Stroke_Count | CLASS A (Novel) | 0.18 | template_width | 3.2% |
| Branch_Point_Count | CLASS B (Partial) | 0.31 | scale | 9.6% |
| Endpoint_Count | CLASS B (Partial) | 0.28 | CoverageAreaScore | 7.8% |
| Stroke_Density | CLASS A (Novel) | 0.15 | VerificationScore | 2.3% |

Stroke_Count was classified as **CLASS A (Novel)** — genuinely independent of all existing pipeline signals. This made it the prime candidate for integration testing.

## 9.5 The Separability Paradox

### 9.5.1 Formulation

Stage 5.8 established that Stroke_Count achieves:
- AUC = 0.951 for separating MR symbols from Dominant FP at the population level
- Cohen's d = 2.647 (nearly 3σ separation)
- Only 5.2% distribution overlap
- Novel signal (not correlated with existing pipeline features)

By every classical metric, Stroke_Count should be an extremely powerful discriminator. The expectation was that integrating it into the scoring formula would dramatically improve ranking quality.

### 9.5.2 The Paradox

As documented in Chapter 10, integrating Stroke_Count as a continuous multiplier produced **zero ranking improvement** and in several experiments **degraded** performance. All experiments that used Stroke_Count-based penalties (EXP_A through EXP_D) performed worse than the BASE experiment that used no structural discriminator at all.

**The paradox**: A feature achieving AUC=0.951 at the population level cannot improve rank ordering when used as a continuous multiplier.

### 9.5.3 Resolution

The resolution lies in the distinction between **population-level separability** and **rank-level discrimination**:

1. **AUC measures** how well two distributions can be separated by a threshold — it answers "can we draw a line between MR and non-MR populations using this feature?"

2. **Rank improvement requires** that the feature's value monotonically orders candidates such that MR symbols score higher than non-MR symbols at every rank position

3. **The failure mode**: While the MR and Dominant FP populations are well-separated in Stroke_Count space, the Hard Negatives (which occupy the same ranking neighborhood as MR symbols) have identical Stroke_Count distributions. Applying a Stroke_Count penalty indiscriminately penalizes both hard negatives and true MR symbols, producing no net ranking change — or worse, promotes candidates from outside the current ranking window that happen to have low Stroke_Count.

This is the most fundamental lesson of the project: **separability ≠ ranking improvement**.

---

*Forensic Source References:*
- *Structural verification: `src/verification/structural_verification.py`*
- *Structural discovery: `exploration/archived/scripts/stage5_8_structural_discovery.py`*
- *Feature separability audit: Referenced as `reports/feature_separability_audit.md`*
- *Discriminator leaderboard: Referenced as `reports/discriminator_leaderboard.md`*
- *Redundancy analysis: Referenced as `reports/discriminator_redundancy_analysis.md`*
- *Master Retrospective Sections: Phase 5.8*
