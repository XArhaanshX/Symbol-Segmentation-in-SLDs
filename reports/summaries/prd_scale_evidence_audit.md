# PRD Scale Range Data-Evidence Audit

This report evaluates the empirical evidence provided within the Technical PRD to justify the defined scale range parameters (`SCALE_MIN = 0.15`, `SCALE_MAX = 0.40`, `N_SCALES = 10`).

---

## 1. Classification: PARTIALLY SUPPORTED

The PRD scale range is classified as **PARTIALLY SUPPORTED**. 

* **Why it is supported**: The PRD provides concrete, dataset-wide measurements of symbol widths in pixels, establishing that the target symbols are significantly smaller than the template.
* **Why it is only partial (and partially assumption-driven)**: 
  1. **Lower Bound Omission**: The PRD's own measurements show that symbols in SLD12 are as small as 15 pixels wide (scale factor of $\approx 0.093$). However, the PRD defines `s_min` as 0.15 (width 24 pixels), which means the search range **fails to cover the smallest observed symbols in the dataset**.
  2. **Upper Bound Inflation**: The PRD's measurements show a maximum width of 50 pixels (scale factor of $\approx 0.311$ in sparse SLDs), but the search range extends to 0.40 (width 64 pixels) without any empirical observation of a symbol that size.
  3. **No Feasibility Calculations for Downsampling**: The PRD contains no calculations or tests verifying whether thin binary edge lines can survive downsampling to 0.15. This led to a silent failure where templates generated at scales 0.150–0.206 are completely empty.

---

## 2. Detailed Audit of PRD Evidence

### A. Dataset Measurements & surveys
* **PRD Findings**: Section 3.3.3 ("Scale Distribution") contains the following empirical width estimates:
  - Dense SLDs (SLD2, 3, 7, 10): **25–40 pixels wide**
  - Sparse SLDs (SLD1, 4): **30–50 pixels wide**
  - SLD12: **15–25 pixels wide**
* **Verification**: The PRD does contain empirical measurements. However, these are expressed as ranges of widths (widths only, no heights) and are labeled as "estimates from visual inspection."

### B. Mathematical Calculations & Discrepancies
Let us calculate the exact scale factors ($s = \frac{\text{Width}_{\text{SLD}}}{\text{Width}_{\text{Template}}}$, where $\text{Width}_{\text{Template}} = 161$ pixels) implied by the PRD's own measurements:

| Category | Measured Widths (px) | Implied Scale Factors ($s$) | Covered by PRD `[0.15, 0.40]`? |
|---|---|---|---|
| Dense SLDs | 25 – 40 | 0.155 – 0.248 | **Yes** (fully covered) |
| Sparse SLDs | 30 – 50 | 0.186 – 0.311 | **Yes** (fully covered) |
| SLD12 | 15 – 25 | 0.093 – 0.155 | **No** (partially missed; 15px to 24px is excluded) |

* **Analysis of Discrepancies**:
  - **The Lower Bound Gap**: Setting `SCALE_MIN = 0.15` excludes symbols in SLD12 that are between 15 and 23 pixels wide (scales 0.093 to 0.143). This represents a direct contradiction: the PRD documents the presence of 15px symbols in SLD12 but recommends a search minimum that cannot detect them.
  - **The Upper Bound Margin**: The maximum observed width is 50px (scale 0.311), but `SCALE_MAX` is set to 0.40. While a safety margin is reasonable (Risk T2), there is no empirical evidence of a 64px symbol in the dataset.
  - **The "3–6×" Size Ratio Calculation**: Section 7.3.1 states that the scale range `[0.15, 0.40]` covers the *"observed 3–6× size ratio."* 
    - A $3\times$ reduction is a scale of $1/3 \approx 0.333$ (template width 53.6px).
    - A $6\times$ reduction is a scale of $1/6 \approx 0.167$ (template width 26.8px).
    - The actual observed range is 15px (10.7× reduction) to 50px (3.2× reduction). The "3–6×" ratio is a simplified approximation that ignores the extreme compact scale of SLD12.

### C. Downsampling Disintegration (The Blind Spot)
* **PRD Claim**: Section 7.3.1 outlines the resizing and thresholding steps:
  > `scaled = cv2.resize(template_edges, (0,0), fx=s, fy=s, interpolation=INTER_AREA)`
  > `_, scaled = cv2.threshold(scaled, 127, 255, THRESH_BINARY)`
* **Evidence Audit**: The PRD contains **no calculations or testing** regarding the interaction between thin-line edges (thickness $\le 2$ pixels), interpolation methods, and hard thresholds. 
* **The Mathematical Reality**: Resizing a thin binary edge line by a factor of 0.15 spreads the single-pixel line intensity across a wider grid via interpolation, causing the peak intensity in the resized image to drop far below 127. Applying a threshold of 127 on this image results in an empty mask. The PRD assumed this operation was valid without checking the output, resulting in empty templates (0 pixels) for scales 0.150 and 0.178, and severe fragmentation for scales 0.206 to 0.261.
