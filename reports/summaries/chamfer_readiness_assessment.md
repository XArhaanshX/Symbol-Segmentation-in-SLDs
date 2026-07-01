# Chamfer Readiness Assessment Report

## Traceability
- **Source Template**: `outputs/template/edges.png`
- **Generation Timestamp**: 2026-06-16T14:45:00Z
- **Scale Set Evaluated**: `[0.093, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400]`
- **Method Evaluated**: Methods A, B, C, D1, D2, D3, E
- **Baseline Metrics Source**: Measured directly from `outputs/template/edges.png` at runtime

---

## 1. Executive Summary

Chamfer Matching computes a distance transform of the query diagram's edge map and matches the template edge coordinates against it. A high-quality Chamfer input template must have:
1. **Continuous Edges**: Broken/fragmented edges degrade the distance transform alignment and increase false match errors.
2. **Stable Geometry**: The relative shape (e.g., circles and lines) must be preserved. While merging components (reduction in $C$) reduces fine structural details, it retains the general geometric silhouette. Fragmentation (increase in $C$), however, shatters the shape, leading to a high rate of false negatives.
3. **No Empty Templates**: Empty templates cause mathematical division-by-zero errors in normalized Chamfer matching.

---

## 2. Suitability Assessment by Method

### Method A (Baseline)
* **Expected Chamfer Robustness**: **Zero**.
* **False Negative Risk**: **100% (Critical)**.
* **Candidate Quality**: Non-functional.
* **Analysis**: Below scale 0.25, the template is empty. Chamfer matching will fail to align any pixels, and normalization will crash. At higher scales, the templates are so fragmented (dots) that the Chamfer distance will be highly sensitive to slight translation/rotation noise, causing matches to be rejected.

### Method B (Binary First)
* **Expected Chamfer Robustness**: Low.
* **False Negative Risk**: High.
* **Candidate Quality**: Poor.
* **Analysis**: Below 0.20, it collapses to 2 components. At larger scales (0.35–0.40), the Canny edge detector applied to the blocky scaled binary produces double-edge artifacts and jagged outlines, resulting in a distorted Chamfer score.

### Method C (Grayscale First)
* **Expected Chamfer Robustness**: Medium.
* **False Negative Risk**: Medium-High.
* **Candidate Quality**: Moderate at small scales, poor at large scales.
* **Analysis**: Method C successfully preserves 8 components at scale 0.15, which is highly impressive. However, its tendency to fragment at scales $\ge 0.25$ ($C \ge 18$, more than double the baseline) introduces severe jaggedness that will degrade Chamfer matching alignment.

### Method D1 (Raw Coordinate Scaling) & D2 (Coordinate Scaling + Reconstruction)
* **Expected Chamfer Robustness**: High.
* **False Negative Risk**: Low.
* **Candidate Quality**: Very Good (Silhouette-level).
* **Analysis**: Since these methods scale the coordinates directly, they never lose pixels due to thresholding. The edges remain continuous and clean. While separate internal components merge due to resolution limits (e.g., $C$ drops to 1 or 2), the structural silhouette is perfectly preserved. Chamfer matching is highly robust to this type of resolution-induced merging because the outer boundaries and major curves are intact.

### Method D3 (Anti-Aliased Subpixel Rasterization)
* **Expected Chamfer Robustness**: High.
* **False Negative Risk**: Low.
* **Candidate Quality**: Excellent.
* **Analysis**: D3 balances coordinate precision with rasterization continuity. By rasterizing on a subpixel grid and downsampling with area interpolation, it creates thick, well-defined continuous edges. At larger scales ($\ge 0.35$), it achieves excellent topological preservation ($C=6$, target $8$). At smaller scales, it merges cleanly into a single continuous shape, preventing any fragmentation.

### Method E (Grayscale Canny)
* **Expected Chamfer Robustness**: Medium-High.
* **False Negative Risk**: Medium.
* **Candidate Quality**: Good.
* **Analysis**: Applying Canny directly to the scaled grayscale image preserves edge continuity better than Method A or B. However, because Canny thresholding depends on local median gradients, it exhibits instability across scales (e.g. collapsing to $C=2$ at scale 0.40 and $C=3$ at 0.35, but holding $C=7$ at 0.25). This instability makes it difficult to rely on for consistent candidate quality.
