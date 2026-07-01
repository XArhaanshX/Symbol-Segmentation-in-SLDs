# PRD Scale Range Provenance Audit

| Audit Detail | Specification |
|---|---|
| **System under Audit** | Symbol Localization System |
| **Audited Parameter** | Template Scale Range (`s_min = 0.15`, `s_max = 0.40`, `N_scales = 10`) |
| **Audit Date** | June 16, 2026 |
| **Formal Classification** | **PARTIALLY SUPPORTED / ASSUMPTION-DRIVEN** |

---

## 1. Executive Summary

This audit performs a forensic investigation into the origin, justification, and validity of the scale range (`0.15` to `0.40`) defined in the Technical PRD. 

While the necessity of multi-scale search is empirically supported by target symbol width measurements (ranging from 15 to 50 pixels across the 10 SLDs), the specific recommended bounds and implementation logic suffer from critical, design-breaking assumptions. 

Specifically, downsampling the template's 1-pixel-thick Canny edge map to factors below `0.23` results in complete topological collapse (empty edge maps or fragmented pixels) under the PRD-defined thresholding logic. Furthermore, the lower bound of `0.15` (width 24 pixels) mathematically fails to cover the smallest observed symbols in SLD12 (width 15 pixels, scale factor `0.093`). 

Rework is mandatory for both the scale bounds and the template preprocessing pipeline before proceeding to Stage 3 (Chamfer Matching).

---

## 2. Scope of Audit

The audit evaluated all sections of `PRD_Symbol_Localization.md` referencing scale, template generation, image properties, and search parameters. It cross-referenced the PRD's theoretical assertions against the empirical findings of the Stage 2.4 validation reports:
* [prd_scale_references.md](file:///c:/Users/arhaa/OneDrive/Symbol%20Segmentor/reports/prd_scale_references.md)
* [prd_scale_rationale_analysis.md](file:///c:/Users/arhaa/OneDrive/Symbol%20Segmentor/reports/prd_scale_rationale_analysis.md)
* [prd_scale_assumption_audit.md](file:///c:/Users/arhaa/OneDrive/Symbol%20Segmentor/reports/prd_scale_assumption_audit.md)
* [prd_scale_evidence_audit.md](file:///c:/Users/arhaa/OneDrive/Symbol%20Segmentor/reports/prd_scale_evidence_audit.md)
* [prd_scale_dependency_analysis.md](file:///c:/Users/arhaa/OneDrive/Symbol%20Segmentor/reports/prd_scale_dependency_analysis.md)

---

## 3. Referenced Sections Summary

The table below summarizes the key sections of the PRD that dictate the system's scale handling:

| PRD Section | Line Number | Content Summary | Purpose |
|---|---|---|---|
| **Sec 2.6 (Non-Assumptions)** | 97 | Defines scale factor distribution as an empirical variable requiring measurement. | Establishes scale as a variable. |
| **Sec 3.3.3 (Scale Distribution)** | 387-397 | Lists observed width estimates for dense (25–40px), sparse (30–50px), and SLD12 (15–25px) diagrams. Concludes scale range is `[0.15, 0.35]`. | Provides the empirical base data. |
| **Sec 7.3.1 (Template Pyramid)** | 1238-1258 | Recommends `s_min=0.15, s_max=0.40, N_scales=10`. Justifies range as covering the "observed 3–6× size ratio." | Defines implementation parameters. |
| **Sec 7.5.2 (Spatial NMS)** | 1420 | Scales NMS suppression radius dynamically: $\text{Radius} = \max(W, H) \cdot s_{\text{best}}$. | Binds scale results to post-processing. |
| **Sec 10.1 (Technical Risks)** | 2077 | Risk T2 (Scale estimation failure) mitigated by a "wide scale range (0.15–0.40) with 10 levels." | Mitigates miscalibration risk. |

---

## 4. Design Rationale Reconstruction

The PRD scale range was derived using a two-step process:
1. **Empirical Measurement**: The author measured symbol widths in the diagrams, obtaining ranges of 15–25px (SLD12), 25–40px (dense), and 30–50px (sparse). Relative to the template width of 161px, these correspond to scale ratios of **0.093 to 0.311**. The author synthesized this as a core range of `[0.15, 0.35]`.
2. **Conservative Expansion**: To mitigate scale misestimation risks (Risk T2) and handle the rendering anomalies of SLD9, the author expanded the upper bound to `0.40` and increased the discretization resolution from 3–5 levels to 10 levels. The lower bound was constrained at `0.15` as a conservative limit to prevent absolute template resolution collapse.

---

## 5. Assumption Audit

| Underlying Assumption | PRD Source | Empirical Validity | Risk Level |
|---|---|---|---|
| **Isotropic Scaling**: Symbols scale uniformly in both dimensions, preserving the aspect ratio of $1.56$. | Sec 2.5, Sec 7.3.1 | **False for SLD9**: The PRD notes in Sec 3.2.2 that SLD9 symbols have a different aspect ratio. | **High** (causes edge mismatch in SLD9) |
| **Geometric Survival**: Resizing thin 1px edge lines to $0.15\times$ and thresholding at 127 preserves topology. | Sec 7.3.1 | **False**: Interpolation spreads pixel intensity; binarization at 127 deletes all pixels below scale 0.20. | **Critical** (causes empty templates in Stage 2) |
| **Discrete Step Sufficiency**: A step size of 0.027 scale factor is fine enough for a 2.0px coverage threshold. | Sec 7.3.1, Sec 7.4.2 | **Medium**: Worst-case discretization error can exceed the 2.0px matching tolerance. | **Medium** (causes false negatives on borderline scales) |

---

## 6. Data-Evidence Discrepancies

A direct comparison of the PRD's empirical measurements against the recommended search range reveals major gaps:

1. **The Lower Bound Gap (Omission)**:
   - Target symbols in SLD12 are documented as being **15–25 pixels wide**, corresponding to a scale factor of **0.093 to 0.155**.
   - The PRD scale range starts at **0.15** (width 24 pixels).
   - *Impact*: Any symbol in SLD12 smaller than 24 pixels is mathematically excluded from the search space, guaranteeing false negatives.
2. **The Upper Bound Margin (Inflation)**:
   - The largest observed symbols are 50 pixels wide (scale **0.311**).
   - The recommended scale maximum is **0.40** (width 64 pixels).
   - *Impact*: The system searches scales from 0.311 to 0.400 unnecessarily, adding $20\%$ overhead to the sliding window runtime without targeting any observed data.

---

## 7. Downstream Architectural Impact

If the lower scales are removed or fail (as they currently do because scales 0.150–0.206 are empty):
* **Chamfer Matching**: Runs faster but fails to detect small symbols. Empty templates produce NaN or zero score basins, leading to false detections or pipeline crashes.
* **Coverage Filter**: Fails with division-by-zero errors when dividing by $|E_T| = 0$ on empty templates.
* **PCA Verification**: If small symbols are matched at larger scales (due to the absence of correct scales), the bounding box will include background clutter. The clutter prevents centroid alignment and raises reconstruction error, causing the PCA stage to reject true symbols.

---

## 8. Recommendations & Rework Plan

The scale range and template generation pipeline **must be reworked** before proceeding. Two paths are available:

### Recommendation A: Rework the Template Generation Pipeline (Highly Recommended)
Rather than changing the scale range to match the broken implementation, fix the implementation so it can support the required scales (down to 0.093):
1. **Grayscale Downsampling**: Downsample the grayscale template (`MR_Symbol.png`) first, and then apply binarization and Canny edge detection to the scaled image. Canny dynamically computes local thresholds, preserving thin-line topology even at small scales.
2. **Vector Scaling**: Extract the template coordinates at full scale ($1.0\times$) as an $N \times 2$ coordinate list, and scale the coordinates directly: $p_{\text{scaled}} = p \cdot s$. This completely eliminates interpolation and thresholding artifacts, preserving 100% of the topology at all scales.

### Recommendation B: Rework the Scale Range Parameters (Alternative)
If the template bank generation pipeline cannot be modified:
1. **Truncate the Lower Bound**: Raise the minimum scale to `SCALE_MIN = 0.23`. This is the lowest scale where the template edge map retains basic connectivity.
2. **Adjust the Upper Bound**: Lower the maximum scale to `SCALE_MAX = 0.32` to eliminate redundant matching above 50 pixels.
3. **Accept Lower Recall**: Acknowledge that symbols in SLD12 (15–25px wide) will be undetected by the classical pipeline.
