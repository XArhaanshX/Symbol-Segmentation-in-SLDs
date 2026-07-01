# PRD Scale References Audit

This report documents every reference in the Technical PRD (`PRD_Symbol_Localization.md`) regarding scale, scaling, template size, pyramid generation, search ranges, and multi-scale processing. The goal is to establish complete traceability for the scale-space search parameters.

---

## 1. Section 2 — Problem Definition (Non-Assumptions)
* **Location**: Section 2.6 (Line 97)
* **Direct Quote**: 
  > `- **Scale range:** Symbol size relative to diagram varies. Exact scale factor distribution requires measurement.`
* **Interpretation**: The PRD explicitly declares that the scale of the target symbol in the SLDs relative to the template is a variable and cannot be assumed a priori. It calls for empirical measurement of the scale factor distribution.
* **Purpose within the Architecture**: Establishes scale variation as an empirical variable that the system must handle dynamically, laying the foundation for a multi-scale search.

---

## 2. Section 2 — Problem Definition (Edge Cases)
* **Location**: Section 2.7 (Line 108)
* **Direct Quote**:
  > `| Scale variation | Different SLDs may render the symbol at different pixel sizes | Multi-scale matching required |`
* **Interpretation**: Scale variation is classified as an operational edge case. The specified mitigation is a multi-scale matching framework.
* **Purpose within the Architecture**: Serves as a high-level requirement that binds the matching engine to support multi-scale inputs.

---

## 3. Section 3 — Dataset Analysis (Target Symbol Properties)
* **Location**: Section 3.1.1 (Lines 54 & 121)
* **Direct Quote**:
  > Line 54: `| Query Symbol | `MR_Symbol.png` — 161×103 pixels, RGBA, grayscale content on fully opaque white background | PNG |`
  > Line 121: `| Dimensions | 161 × 103 pixels (W × H) |`
* **Interpretation**: The reference query template has fixed dimensions of 161 × 103 pixels.
* **Purpose within the Architecture**: Defines the baseline template size from which all downscaling factor calculations and relative template sizes are derived.

---

## 4. Section 3 — Dataset Analysis (Candidate Descriptors Evaluation)
* **Location**: Section 3.1.4 (Line 171)
* **Direct Quote**:
  > `| Shape Context | Medium | Captures spatial distribution of edge points, but sensitive to scale |`
* **Interpretation**: Shape Context is evaluated as only moderately suitable because of its sensitivity to scale changes.
* **Purpose within the Architecture**: Explains why Shape Context is rejected as a primary descriptor in favor of edge-domain Chamfer matching combined with an explicit scale search.

---

## 5. Section 3 — Dataset Analysis (Individual SLD Characteristics)
* **Location**: Section 3.2.2 (Lines 215, 281, 311, 313, 359)
* **Direct Quotes**:
  > Line 215 (SLD1): `- **Potential FN sources**: The vertically-oriented CT on the branch below may have different scale`
  > Line 281 (SLD7): `- **Potential FN sources**: Scale variation between sections possible`
  > Line 311 (SLD9): `- **Important**: This SLD has a visually different rendering style — the CT symbols appear to have a different scale and aspect ratio relative to the bus structure`
  > Line 313 (SLD9): `- **Potential FN sources**: Different scale may cause template mismatch`
  > Line 359 (SLD12): `- **Potential FN sources**: Small image size may cause scale issues`
* **Interpretation**: Forensic analysis of individual SLDs reveals several scale-related vulnerabilities:
  - Local scale variations within a single diagram (SLD1, SLD7).
  - Systematic scale differences due to alternative rendering styles (SLD9).
  - Extreme downscaling due to low image resolution (SLD12).
* **Purpose within the Architecture**: Highlights the risk of False Negatives (FN) if the scale search range is too narrow or lacks sufficient resolution.

---

## 6. Section 3 — Dataset Analysis (Dataset-Wide Scale Distribution)
* **Location**: Section 3.3.3 (Lines 387–397)
* **Direct Quote**:
  > ### 3.3.3 Scale Distribution
  > The MR symbol template is 161×103 pixels. The actual symbol size in diagrams varies:
  > - In dense SLDs (SLD2, SLD3, SLD7, SLD10): symbols appear approximately **25–40 pixels wide** — roughly 4–6× smaller than the template.
  > - In sparse SLDs (SLD1, SLD4): symbols appear approximately **30–50 pixels wide** — roughly 3–5× smaller than the template.
  > - In SLD9: symbols appear at a potentially different scale due to the different rendering style.
  > - In SLD12: symbols appear approximately **15–25 pixels wide** due to the very compact image.
  > 
  > **Conclusion**: Scale variation is moderate (estimated 0.15–0.35× of template). Multi-scale matching is required with approximately 3–5 scale levels. Requires empirical calibration.
* **Interpretation**: This is the core empirical dataset-wide analysis of scale. The author estimates the width of the symbols in the target diagrams:
  - Dense: 25–40 px wide (Scale ratio ≈ 0.155–0.248)
  - Sparse: 30–50 px wide (Scale ratio ≈ 0.186–0.311)
  - SLD12: 15–25 px wide (Scale ratio ≈ 0.093–0.155)
  The conclusion estimates the range as **0.15–0.35×** and recommends **3–5 scale levels**.
* **Purpose within the Architecture**: Establishes the empirical base measurements that justify the scale range.

---

## 7. Section 3 — Dataset Analysis (Dataset Weaknesses & Risks)
* **Location**: Section 3.3.6 (Line 421) and Section 3.3.7 (Line 431, 432)
* **Direct Quotes**:
  > Line 421: `2. **Scale variation** — the template is significantly larger than the actual symbols in diagrams.`
  > Line 431: `3. **Scale miscalibration**: The 4–6× scale difference between template and diagram symbols means scale estimation errors directly impact recall.`
  > Line 432: `4. **SLD9 anomaly**: The visually different rendering style of SLD9 may require special handling or a wider scale search range.`
* **Interpretation**: Confirms scale mismatch as a primary risk to recall and flags SLD9 as requiring potential expansion of the search range.
* **Purpose within the Architecture**: Drives the architecture to incorporate conservative margins in the scale range and sufficient levels of scale discretization.

---

## 8. Section 3 — Dataset Analysis (Expected Failure Modes)
* **Location**: Section 3.3.9 (Lines 448 & 451)
* **Direct Quotes**:
  > Line 448: `2. **Missed detections at extreme scales**: If the scale search range is too narrow, symbols in SLD12 (very small) or SLD1 (potentially larger) may be missed.`
  > Line 451: `5. **Template-to-diagram scale mismatch**: The 161×103 template rendered at the wrong scale will produce poor Chamfer scores everywhere.`
* **Interpretation**: Warns that an overly narrow scale search range will lead to missed detections on SLD12 (small end) or SLD1 (large end), and emphasizes that incorrect scale matching will severely degrade Chamfer scores.
* **Purpose within the Architecture**: Justifies expanding the scale range and increasing the number of scale steps.

---

## 9. Section 4 — Literature Survey
* **Location**: Sections 4.1, 4.2, 4.3, 4.23 (Lines 500, 510, 542, 857, 861)
* **Direct Quotes**:
  > Line 500 (NCC): `The template is 161×103 pixels while diagram symbols are ~25–40 pixels. The 4–6× scale mismatch makes direct NCC fail entirely.`
  > Line 510 (Multi-Scale NCC): `Applies NCC at multiple scale levels by resizing the template to a pyramid of scales...`
  > Line 542 (Chamfer): `- **No inherent scale invariance** — requires multi-scale search.`
  > Line 861 (Hybrid): `- Multi-scale search → scale invariance`
* **Interpretation**: Standard single-scale matching is rejected due to the scale mismatch. Multi-scale search wrappers are identified as the mandatory solution to provide scale invariance.
* **Purpose within the Architecture**: Validates the architectural choice of wrapping the core matching method (Chamfer) in a multi-scale search.

---

## 10. Section 5 — Architecture Trade Study
* **Location**: Sections 5.1 & 5.2 (Lines 890 & 902)
* **Direct Quotes**:
  > Line 890: `| **Scale handling** | High | 4–6× scale mismatch between template and diagram symbols |`
  > Line 902: `| Multi-Scale NCC | ✅ | ✅ | ... |`
* **Interpretation**: Scale handling is assigned a "High" weight, confirming that any acceptable architecture must support multi-scale processing.
* **Purpose within the Architecture**: Establishes scale handling as a critical evaluation criterion for the system selection.

---

## 11. Section 6 — Architecture & Justification
* **Location**: Sections 6.1 & 6.2 (Lines 1017, 1029, 1075)
* **Direct Quotes**:
  > Line 1017: `Multi-Scale Multi-Orientation Chamfer Matching with PCA Subspace Verification`
  > Line 1029: `MULTI-SCALE CHAMFER LOCALIZATION`
  > Line 1075: `**Why multi-scale**: The template is 161×103 pixels; diagram symbols are ~25–40 pixels. Without multi-scale search, the scale mismatch guarantees failure.`
* **Interpretation**: Multi-scale search is explicitly incorporated into the primary localization stage.
* **Purpose within the Architecture**: Re-justifies the inclusion of a scale pyramid to bridge the massive template-to-diagram scale discrepancy.

---

## 12. Section 7 — Detailed Pipeline Design (Stage 2a: Template Scale Pyramid)
* **Location**: Section 7.3.1 (Lines 1238–1258)
* **Direct Quote**:
  > **Purpose**: Generate multiple scaled versions of the template edge map to handle the 4–6× scale mismatch.
  > **Algorithm**:
  > 1. Define scale range: `scales = np.linspace(s_min, s_max, N_scales)`
  >    - Recommended: `s_min=0.15, s_max=0.40, N_scales=10`
  >    - This produces templates from ~24×15 to ~64×41 pixels
  > ...
  > **Mathematical justification**: The scale range [0.15, 0.40] covers the observed 3–6× size ratio between template and diagram symbols. Ten scale levels provide sufficient resolution to find a good match without excessive computational cost.
* **Interpretation**: This is the definitive specification of the scale range. It defines:
  - `s_min` = 0.15
  - `s_max` = 0.40
  - `N_scales` = 10
  It translates these factors into absolute pixels (~24×15 to ~64×41). It justifies the range by saying it covers the "observed 3–6× size ratio."
* **Purpose within the Architecture**: Provides the exact operational parameters and implementation logic for generating the template bank in Stage 2.

---

## 13. Section 7 — Detailed Pipeline Design (NMS Suppression & Bounding Boxes)
* **Location**: Sections 7.5.2 & 7.5.3 (Lines 1420 & 1426)
* **Direct Quotes**:
  > Line 1420: `SUPPRESSION_RADIUS: Set to max(template_width, template_height) * best_scale — approximately the size of the detected symbol.`
  > Line 1426: `Bounding box (x, y, w, h) — derived from template size at the best-matching scale`
* **Interpretation**: Bounding box extraction and NMS suppression radius are dynamically parameterized by the best-matching scale detected in Stage 3.
* **Purpose within the Architecture**: Directly links the scale-search results to the post-processing stages, ensuring bounding boxes match the physical symbol size.

---

## 14. Section 7 — Detailed Pipeline Design (PCA Verification & Ensemble)
* **Location**: Sections 7.6.1 & 7.8 (Lines 1446 & 1581)
* **Direct Quotes**:
  > Line 1446 (PCA Augmentation): `1. **Scale variations**: [0.90, 0.95, 1.00, 1.05, 1.10] — 5 levels`
  > Line 1581 (Ensemble): `Enhance recall by generating a small ensemble of template variants (scale, erosion/dilation...`
* **Interpretation**: Local scale variations are used to construct the PCA appearance manifold (Stage 5a) and the optional template ensemble (Stage 5b) to enhance matching robustness.
* **Purpose within the Architecture**: Mitigates discretization errors in the 10-level scale pyramid by introducing local scale jittering.

---

## 15. Section 8 & 10 — Code Configuration & Risks
* **Location**: Section 8.2.1 (Lines 1685-1687), Section 8.4 (Lines 1860-1861), Section 10.1 (Line 2077)
* **Direct Quotes**:
  > Line 1685: `SCALE_MIN = 0.15`, `SCALE_MAX = 0.40`, `N_SCALES = 10`
  > Line 2077 (Risk Mitigation): `Use a wide scale range (0.15–0.40) with 10 levels.`
* **Interpretation**: Hardcodes the scale range parameters into the default system configuration files and lists it as the primary mitigation for scale misestimation risk.
* **Purpose within the Architecture**: Ensures the recommended range [0.15, 0.40] is the default active configuration for the pipeline execution.
