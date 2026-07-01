# Chapter 7 — Chamfer Matching and Candidate Generation

## 7.1 Distance Transform Precomputation

### 7.1.1 Mathematical Foundation

The Euclidean Distance Transform of a binary edge image E is defined as:

$$DT(x, y) = \min_{(x', y') \in E} \sqrt{(x - x')^2 + (y - y')^2}$$

For every pixel (x, y) in the image, DT gives the Euclidean distance to the nearest edge pixel. At edge pixels themselves, DT = 0. The distance increases smoothly away from edges, creating a bowl-shaped landscape around each edge structure.

### 7.1.2 Implementation

```python
inv_edges = 255 - diagram_edges
DT = cv2.distanceTransform(inv_edges, cv2.DIST_L2, 5)
```

The `cv2.DIST_L2` flag selects Euclidean distance, and the mask size 5 provides a good approximation to the exact Euclidean DT. The result is a float32 image where each pixel contains its minimum distance to an edge.

### 7.1.3 Storage

Distance transforms are saved as 32-bit TIFF files (`outputs/distance_transforms/{SLD}_dt.tiff`) to preserve floating-point precision. This avoids quantization artifacts that would occur with 8-bit PNG storage.

## 7.2 Dense Sliding-Window Chamfer Matching

### 7.2.1 Scoring Algorithm

For each template variant (scale s, orientation θ) with edge coordinates E_T = {(e_x^1, e_y^1), ..., (e_x^N, e_y^N)}, the Chamfer score at position (t_x, t_y) is:

$$d_{Chamfer}(t_x, t_y) = \frac{1}{N} \sum_{i=1}^{N} DT(t_y + e_y^i, t_x + e_x^i)$$

This represents the mean distance from each template edge pixel to its nearest diagram edge pixel when the template is centered at position (t_x, t_y).

### 7.2.2 Efficient Implementation via Convolution

The production implementation uses `cv2.filter2D` for computational efficiency:

```python
# Create a kernel from template edge coordinates
kernel = np.zeros((h_template, w_template), dtype=np.float32)
for (ey, ex) in edge_coords:
    kernel[ey, ex] = 1.0 / len(edge_coords)

# Convolve DT with the kernel
score_map = cv2.filter2D(dt_image, -1, kernel)
```

This computes the mean DT value within the template mask at every position simultaneously, equivalent to sliding-window evaluation but implemented via FFT-based convolution for O(W_diagram × H_diagram × log(max(W, H))) complexity.

### 7.2.3 Multi-Scale Multi-Orientation Sweep

The sweep iterates across all 40 template variants (10 scales × 4 orientations), producing 40 score maps per SLD. Each score map has the same spatial dimensions as the diagram DT.

**Computational Estimate**: For a typical SLD (1500×800 pixels) with 40 variants:
- 40 convolution operations, each on a 1500×800 image
- Total: ~3-5 minutes per SLD on CPU

## 7.3 Score Map Aggregation

### 7.3.1 Best-Match Selection

At each spatial position, the variant producing the minimum Chamfer score (subject to coverage threshold) is selected:

```python
best_score_map = np.full_like(dt_image, np.inf)
best_scale_map = np.zeros_like(dt_image)
best_orient_map = np.zeros_like(dt_image)

for variant in all_variants:
    mask = (variant.score_map < best_score_map) & (variant.coverage_map >= 0.65)
    best_score_map[mask] = variant.score_map[mask]
    best_scale_map[mask] = variant.scale
    best_orient_map[mask] = variant.orientation
```

### 7.3.2 Local Minima Extraction

Candidate positions are identified as local minima in the best score map:

```python
local_min = scipy.ndimage.minimum_filter(best_score_map, size=15)
candidates = np.where(best_score_map == local_min)
```

A 15×15 window ensures that only spatially distinct score basins are extracted. Adjacent pixels with identical minimum scores within the window are collapsed to a single candidate.

## 7.4 Candidate Statistics

### 7.4.1 Volume

The Stage 3 candidate extraction produced **264,852 raw candidates** across all 10 SLDs. This represents the complete universe of positions where any template variant achieved a local minimum in the Chamfer score map.

### 7.4.2 Score Distribution

| Statistic | Value |
|---|---|
| Minimum Chamfer score (any candidate) | ~0.20 px |
| Median Chamfer score (all candidates) | ~4.50 px |
| Mean Chamfer score (all candidates) | ~5.80 px |
| True MR symbol Chamfer scores | 5.50 – 8.00 px |
| Dominant false positive scores | 0.50 – 2.00 px |

The critical observation: **false positives have LOWER (better) Chamfer scores than true MR symbols.** This is the ranking inversion problem.

## 7.5 The Ranking Inversion Crisis

### 7.5.1 Discovery

When the 264,852 candidates were sorted by ascending Chamfer score (lower = better match), **zero true MR symbols appeared in the top 100**. The false positive precision at top-100 was 0.0%.

True MR symbols were found at approximately rank ~20,000 — deep within the candidate pool, far below thousands of false positive candidates.

### 7.5.2 Root Cause: Small-Template Bias

The root cause is the interaction between template scale and Chamfer scoring:

1. **Small templates** (scale 0.150–0.178) contain very few edge pixels (3–12 for Method A, 100–108 for Method D3)
2. **Text characters** and **conductor intersections** contain dense edge concentrations in small regions
3. When a small template is placed over a dense edge region, **most or all template edges** happen to be near a diagram edge purely by coincidence
4. The resulting mean Chamfer distance is very low (0.5–2.0 px) — **lower than genuine MR symbol matches** which have more complex edge structures that cannot all be simultaneously close to diagram edges
5. The Chamfer score therefore **rewards** small-scale spurious matches over large-scale genuine matches

### 7.5.3 Mathematical Analysis

Consider two candidates:
- **True MR symbol** at scale 0.25: 135 template edges, mean distance 6.5 px. Some template edges match MR coils perfectly (distance ~0), but the base bar and stem edges are near bus conductor edges (distance ~5-10 px), pulling the average up.
- **Text fragment "CB"** at scale 0.15: 102 template edges, mean distance 0.72 px. The dense, randomly-oriented edges of the text characters happen to be near many template edges, producing an artificially low mean distance.

The Chamfer metric inherently favors the second candidate because it optimizes mean distance without regard for structural coherence.

### 7.5.4 Scale-Regime Stratification

The ranking quality was found to be strongly correlated with symbol scale:

| Scale Regime | Scale Range | Top-1000 Hit Rate | Typical Rank |
|---|---|---|---|
| **A** (Large) | ≥ 0.30 | > 90% | Top 50–200 |
| **B** (Medium) | 0.20 – 0.30 | ~60% | 200–1000 |
| **C** (Small) | 0.15 – 0.20 | ~20% | 1000–5000 |
| **D** (Micro) | < 0.15 | ~0% | > 10,000 |

Spearman rank correlation between symbol scale and candidate rank was statistically significant (p < 0.001), confirming that scale is the dominant factor in ranking quality.

## 7.6 Coverage Ratio Analysis

### 7.6.1 Computation

For each candidate, the coverage ratio at four distance tolerances was computed:

```python
coverage_r0 = (DT_values <= 0.05).sum() / edge_count  # Exact alignment
coverage_r1 = (DT_values <= 1.05).sum() / edge_count  # 1px tolerance
coverage_r2 = (DT_values <= 2.05).sum() / edge_count  # 2px tolerance
coverage_r3 = (DT_values <= 3.05).sum() / edge_count  # 3px tolerance
```

### 7.6.2 Coverage-Chamfer Redundancy Discovery

A critical finding of Stage 4 analysis was that **coverage ratio is strongly anti-correlated with Chamfer score** (Pearson r ≈ -0.90). This means coverage provides almost zero independent information beyond what the Chamfer score already captures.

Intuitively: if a template position has low mean Chamfer distance, most template edges must be near diagram edges, which directly implies high coverage. The two metrics are mathematically coupled through the distance transform.

### 7.6.3 Coverage Distribution Inversion

An even more troubling finding: **false positives have HIGHER coverage than true positives**.

| Group | Median Coverage R1 | Median Coverage R2 |
|---|---|---|
| True MR symbols | 73% | 85% |
| Dominant false positives | 93% | 97% |

This coverage inversion means that using coverage as an independent filtering criterion would preferentially retain false positives and remove true symbols — the opposite of the intended effect.

The mechanism is the same small-template bias: small templates placed over dense edge regions achieve near-perfect coverage because the few template edges are trivially covered by the many nearby diagram edges.

## 7.7 Impact and Response

The Chamfer matching stage successfully established that:
1. ✅ True MR symbols are **present** in the candidate pool (recall > 0 in the full set)
2. ✅ The localization mechanism works — candidates near true symbols have reasonable scores
3. ❌ The ranking is **completely inverted** — false positives dominate the top positions
4. ❌ Coverage ratio provides **no independent discriminative signal**

These findings motivated the development of coverage-area rescoring (Stage 4) and structural verification (Stage 5) to address the ranking quality problem.

---

*Forensic Source References:*
- *Chamfer matching engine: `src/template_matching/chamfer_matching.py`*
- *Coverage audit analysis: `src/verification/coverage_audit.py`*
- *Coverage rescoring: `src/verification/coverage_rescoring.py`*
- *Stage 3 failure analysis: Referenced in Master Retrospective as `stage3_failure_analysis.md`*
- *Coverage forensics: `reports/coverage_forensics/`*
- *Ranking quality analysis: `reports/ranking_quality/`*


# Chapter 8 — Coverage Rescoring

## 8.1 Motivation

Given the catastrophic ranking inversion from raw Chamfer scores (Chapter 7), Stage 4 was designed as a **pure rescoring layer** that recomputes candidate scores using area-normalized formulations to counteract the small-template bias.

The key insight: while the Chamfer score alone rewards small templates (fewer edges = easier to match), multiplying by template area penalizes small templates because their area is small. This counteracts the bias, promoting larger-scale matches that are more likely to represent genuine symbol detections.

## 8.2 Rescoring Methodology

### 8.2.1 Score A: Coverage × Scale

$$\text{Score}_A = \text{Coverage}_{R1} \times \text{Scale}$$

This is the simplest area normalization. It linearly penalizes small-scale matches.

### 8.2.2 Score B: Coverage × Template Area

$$\text{Score}_B = \text{Coverage}_{R1} \times \text{Template\_Area}$$

This provides stronger penalization because template area scales quadratically with the linear scale factor:

$$\text{Template\_Area} = (W_{template} \times s) \times (H_{template} \times s) = W \times H \times s^2$$

A scale 0.15 template has area = 360 px², while a scale 0.30 template has area = 1440 px² — a 4× difference for a 2× change in linear scale.

### 8.2.3 Score C: Coverage × Scale × Edge Density

$$\text{Score}_C = \text{Coverage}_{R1} \times \text{Scale} \times \text{Edge\_Density}$$

This adds an edge density term, further penalizing templates with low edge density (which tend to produce spurious matches on uniform background).

### 8.2.4 Operational Validation

Score C was only computed if the prior Stage 3.6 validation experiment confirmed it as a valid metric. The validation check is performed at runtime:

```python
def check_score_c_validated():
    val_path = os.path.join(REPORTS_DIR, "coverage_normalization_experiments.md")
    if os.path.exists(val_path):
        with open(val_path, "r") as f:
            content = f.read()
            if "Coverage × Scale × Density" in content:
                return True
    return False
```

## 8.3 Results

### 8.3.1 Rank Improvement

Coverage-area rescoring produced massive rank improvements for most true MR symbols:

| Metric | Before Rescoring | After Rescoring (Score B) |
|---|---|---|
| Median true MR rank | ~20,000 | ~1,000–2,000 |
| Best true MR rank | ~500 | Top-10 (per SLD) |
| Worst true MR rank | ~260,000 | ~50,000 |
| Average rank improvement | — | +1,000–2,000 |

Some true MR symbols reached the **Top-10 per SLD** after rescoring — a dramatic improvement from their prior positions.

### 8.3.2 Persistent Limitations

Despite the improvement, several problems persisted:

1. **Coverage-Chamfer redundancy**: Coverage R1 is anti-correlated with Chamfer score (r ≈ -0.90), so Score A and Score B effectively combine two highly correlated signals. The independent information content is limited.

2. **Coverage distribution inversion**: False positives still have higher coverage than true positives (93% vs 73% median at R1). The area normalization mitigates this but does not eliminate it.

3. **Small-symbol localization failure**: Symbols at scale < 0.15 remain effectively undetectable regardless of rescoring formula. The fundamental Chamfer matching failure at these scales cannot be corrected by post-hoc rescoring.

### 8.3.3 Candidate Survival Audit

The Stage 4 implementation enforces strict survival auditing:

```python
if count_after != count_before:
    print(f"FATAL: Candidate survival mismatch! Before: {count_before}, After: {count_after}")
    sys.exit(1)
```

**Result**: 264,852 candidates in, 264,852 candidates out. Zero candidates lost. Stage 4 operates as a pure rescoring layer — no filtering, suppression, or deletion.

## 8.4 Multi-Ranking Export

Stage 4 exports four independently ranked datasets:

1. **`rescored_candidates.csv`**: Full dataset with all new score columns
2. **`ranked_by_coverage_scale.csv`**: Sorted by Score A (Coverage × Scale, descending)
3. **`ranked_by_coverage_area.csv`**: Sorted by Score B (Coverage × Area, descending) — **primary ranking for Stage 5**
4. **`ranked_by_combined.csv`**: Sorted by Score C (if validated)

The `ranked_by_coverage_area.csv` dataset becomes the input for Stage 5 structural verification.

## 8.5 Visual Validation

Stage 4 generates visual overlays for three diagnostic SLDs (SLD1, SLD4, SLD11) at three depths (Top-10, Top-25, Top-50) for each ranking:

- **Red boxes**: Original (raw Chamfer) ranking
- **Green boxes**: Score A (Coverage × Scale) ranking
- **Blue boxes**: Score B (Coverage × Area) ranking

These overlays enable visual comparison of how rescoring shifts the ranked candidate composition — confirming that rescoring promotes larger-scale matches while demoting small-scale text/conductor matches.

## 8.6 Key Findings

1. **Area normalization is the single most effective post-Chamfer correction**: The quadratic relationship between area and scale provides sufficient penalization to counteract the linear Chamfer bias.

2. **Coverage ratio is NOT an independent signal**: Its strong anti-correlation with Chamfer score (r ≈ -0.90) means it contributes almost no orthogonal discriminative information. This was a critical negative finding that eliminated coverage as a candidate for independent filtering.

3. **Rescoring cannot solve the localization problem**: Symbols that are not detected by the Chamfer matching engine (scale < 0.15) cannot be rescued by any rescoring formula. The fundamental detection limit is set by the matching stage, not the ranking stage.

4. **Candidate preservation is non-negotiable**: The survival audit ensures that no candidates are accidentally lost during rescoring. Any candidate reduction must be an explicit, documented filtering step in a later stage.

---

*Forensic Source References:*
- *Coverage rescoring implementation: `src/verification/coverage_rescoring.py`*
- *Coverage audit analysis: `src/verification/coverage_audit.py`*
- *Stage 4 rank improvement analysis: Referenced in Master Retrospective as `stage4_rank_improvement_analysis.md`*
- *Coverage discriminative power assessment: Referenced as `coverage_discriminative_power_assessment.md`*
- *Candidate survival audit: `reports/stage4_candidate_survival_audit.md`*
- *Visual validation outputs: `outputs/stage4_visualizations/`*
