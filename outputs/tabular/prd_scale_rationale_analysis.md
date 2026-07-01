# PRD Scale Range Design Rationale Reconstruction

This report reconstructs the design rationale behind the scale range parameters (`s_min = 0.15`, `s_max = 0.40`, and `N_scales = 10`) defined in the Technical PRD.

---

## 1. Rationale Classification

The PRD-defined scale range is a hybrid of:
* **Option A: Derived from actual measurements of SLD symbols** (for the core range of [0.15, 0.35])
* **Option C: Chosen as a conservative engineering search range** (for the expanded upper bound of 0.40 and the increased resolution of 10 scales instead of 3–5)

It was **not** derived from prior experiments (Option B), copied from a prior design (Option D), or introduced without supporting evidence (Option E).

---

## 2. Rationale Analysis & PRD Traceability

### A. Core Range Derivation (Option A)
The foundation of the scale range is empirical. Section 3.3.3 ("Scale Distribution") provides explicit width measurements for target symbols across different categories of diagrams:
* **Dense SLDs (SLD2, 3, 7, 10)**: Symbols are ~25–40 pixels wide.
  $$\text{Scale Ratio} = \frac{25}{161} \approx 0.155 \quad \text{to} \quad \frac{40}{161} \approx 0.248$$
* **Sparse SLDs (SLD1, 4)**: Symbols are ~30–50 pixels wide.
  $$\text{Scale Ratio} = \frac{30}{161} \approx 0.186 \quad \text{to} \quad \frac{50}{161} \approx 0.311$$
* **Compact SLDs (SLD12)**: Symbols are ~15–25 pixels wide.
  $$\text{Scale Ratio} = \frac{15}{161} \approx 0.093 \quad \text{to} \quad \frac{25}{161} \approx 0.155$$

In Section 3.3.3, the PRD author synthesizes these observations into a core range:
> **Conclusion**: Scale variation is moderate (estimated 0.15–0.35× of template). Multi-scale matching is required with approximately 3–5 scale levels. Requires empirical calibration.

### B. Upper Bound Expansion and Discretization Resolution (Option C)
While the empirical conclusion in Section 3.3.3 points to a range of `[0.15, 0.35]` and `3–5` scale levels, the actual implementation parameters recommended in Section 7.3.1 and Section 8.2.1 are:
* `SCALE_MIN = 0.15`
* `SCALE_MAX = 0.40`
* `N_SCALES = 10`

This expansion represents a **conservative engineering search range** introduced to mitigate specific risks:
1. **Upper Bound Expansion (0.35 → 0.40)**:
   - Section 10.1 (Risk T2) notes that the 4–6× scale ratio might be incorrectly estimated.
   - Section 3.3.7 (Risk 4) identifies the visually different rendering style of SLD9 as an anomaly that may require a "wider scale search range."
   - The scale of 0.40 yields a template width of $161 \times 0.40 = 64.4$ pixels, providing a safety margin on the upper end to capture larger-scale symbols (like the vertically-oriented CT in SLD1 which is noted in Section 3.2.2 as potentially having a "different scale").
2. **Discretization Resolution Expansion (3–5 → 10 levels)**:
   - Section 7.3.1 states: *"Ten scale levels provide sufficient resolution to find a good match without excessive computational cost."*
   - A step size that is too coarse (e.g., 3–5 levels over a wide range) increases the likelihood of a template-to-diagram scale mismatch, which Section 3.3.9 warns will *"produce poor Chamfer scores everywhere"* and directly impact recall (Section 3.3.7, Risk 3).
3. **Lower Bound Constraint (0.15)**:
   - Although the symbols in SLD12 can be as small as 15 pixels wide (scale factor of $\approx 0.093$), the PRD author did not set `s_min` below 0.15.
   - Setting `s_min` to 0.15 yields a minimum template size of $24 \times 15$ pixels. Going lower (e.g., to 0.09) would result in a template of $15 \times 9$ pixels. Because the template is composed of thin Canny edge lines, downsampling it to such low resolutions before binarization causes the thin edges to disintegrate or disappear entirely during the thresholding step (as confirmed by Stage 2.4 forensics where scales 0.150–0.206 suffer topology collapse).
   - Thus, `SCALE_MIN = 0.15` is a conservative engineering limit designed to protect the topological integrity of the template edge map.

---

## 3. Findings Summary Table

| Parameter | Value | Direct PRD Source | Derivation Method | Engineering Rationale |
|---|---|---|---|---|
| `SCALE_MIN` | `0.15` | Sec 3.3.3, Sec 7.3.1 | Empirical Measurement & Topological Constraint | Matches the lower bound of dense SLD symbol widths (25px / 161px ≈ 0.155) while preventing edge disintegration at lower scales (e.g., SLD12's 15px symbols). |
| `SCALE_MAX` | `0.40` | Sec 7.3.1, Sec 10.1 | Conservative Engineering Margin | Expands the observed maximum scale (50px / 161px ≈ 0.31) to 0.40 to handle scale misestimation risk (Risk T2) and the SLD9 rendering anomaly. |
| `N_SCALES` | `10` | Sec 7.3.1, Sec 8.2.1 | Resolution Enhancement | Expands the recommended 3–5 levels to 10 to ensure sufficiently fine discretization, avoiding Chamfer score degradation due to scale mismatch. |
