# PRD Scale Range Assumption Audit

This audit identifies and evaluates the underlying assumptions that must be true for the PRD-defined scale range and template generation parameters (`SCALE_MIN = 0.15`, `SCALE_MAX = 0.40`, `N_SCALES = 10`) to be valid.

---

## 1. Assumption: Isotropic (Uniform) Symbol Scaling
* **Location in PRD**: Section 2.5 (Assumption 2), Section 3.1.1, and Section 7.3.1 (resizing algorithm specifies `fx=s, fy=s` using uniform scaling).
* **Description**: It is assumed that the target symbols in all target SLDs have been scaled uniformly in both horizontal and vertical dimensions, thereby preserving the original template aspect ratio of $1.563$ ($161 \times 103$ pixels).
* **Evidence Provided**: None. The PRD lists the dimensions of the reference template ($161 \times 103$) and estimates the width of the symbols in target diagrams (e.g., 25–40px, 30–50px) but does not provide height measurements of the target symbols in any SLD.
* **Evidence Missing**: Height measurements of the target symbols across the SLDs to verify aspect ratio consistency.
* **Risk Level**: **High**. 
  - **Justification**: Section 3.2.2 explicitly notes that SLD9 contains symbols with a *"visually different rendering style — the CT symbols appear to have a different scale and aspect ratio relative to the bus structure."* 
  - If a symbol has anisotropic scaling (e.g., stretched horizontally or compressed vertically), matching it against an isotropically scaled template will result in significant edge mismatch, causing the Chamfer score to degrade and potentially fall below the coverage filter threshold.

---

## 2. Assumption: Geometric Integrity of Template Edges under Downsampling
* **Location in PRD**: Section 7.3.1 (Algorithm steps 1 and 2, which recommended `s_min = 0.15` and thresholding downsampled images at a constant value of 127).
* **Description**: It is assumed that downsampling thin binary edge lines (1–2 pixels thick) by scale factors as small as $0.15\times$ (a $6.6\times$ size reduction) and then binarizing the interpolated result with a hard threshold of 127 will preserve the distinctive shape characteristics of the MR symbol (two semicircular lobes, vertical stem, T-cap).
* **Evidence Provided**: None. Section 7.3.1 simply states: *"This produces templates from ~24×15 to ~64×41 pixels... covers the observed 3–6× size ratio."*
* **Evidence Missing**: No empirical testing or mathematical modeling was conducted to verify whether edge maps survive resizing and binarization at these scales.
* **Risk Level**: **Critical**.
  - **Justification**: In digital image processing, downsampling thin binary lines using interpolation (such as `INTER_AREA` or `INTER_LINEAR`) spreads the pixel intensities. If the downsampling factor is very high (e.g., $0.15\times$), the peak intensity of the interpolated lines will fall below the hard threshold of 127. 
  - Subsequent forensic validation revealed:
    - Scales $0.150–0.206$: **TOPOLOGY FAILURE** (the template is completely empty, containing 0 edge pixels).
    - Scales $0.233–0.261$: **PARTIAL DEGRADATION** (severe fragmentation and disconnected pixel components).
  - Chamfer matching cannot function with empty or fragmented templates. This assumption is mathematically and empirically false, making the lower end of the PRD scale range invalid without altering the template generation pipeline.

---

## 3. Assumption: Absence of Resolution or Scan Distortions (Digital-Only work)
* **Location in PRD**: Section 2.5 (Assumption 4): *"SLDs are digitally generated (not scanned), resulting in clean line work."*
* **Description**: It is assumed that target images have no scanning artifacts, perspective distortion, geometric skew, or local DPI variations that could alter the scale or geometry of symbols dynamically across a single document.
* **Evidence Provided**: Section 3.2.1 lists low dark-pixel ratios (1.35%–4.02%) and perfect binary contrast. Section 3.2.2 notes "No skew" and "No scan artifacts" for all individual SLDs.
* **Evidence Missing**: None. Visual inspection of the 10 target diagrams confirms they are vector-derived exports.
* **Risk Level**: **Low**.
  - **Justification**: Since the images are direct digital exports, they do not suffer from physical scanning distortions.

---

## 4. Assumption: Discrete Scale Sampling Sufficiency
* **Location in PRD**: Section 7.3.1 (Algorithm step 1 and Mathematical Justification) and Section 7.4.2 (coverage distance threshold $\tau = 2.0$ pixels).
* **Description**: It is assumed that partitioning the scale space into 10 linear divisions between 0.15 and 0.40 (step size of $\approx 0.027$) is sufficiently fine to ensure that at least one discrete template scale will match the actual symbol scale in the diagram within the $\tau = 2.0$ pixel coverage tolerance.
* **Evidence Provided**: Section 7.3.1 states: *"Ten scale levels provide sufficient resolution to find a good match without excessive computational cost."*
* **Evidence Missing**: Mathematical verification of the worst-case alignment error as a function of the scale step size ($0.027$) and the template dimensions ($161 \times 103$).
* **Risk Level**: **Medium**.
  - **Justification**: If a symbol's actual scale in the diagram lies exactly between two steps (e.g., scale 0.192, where the nearest steps are 0.178 and 0.206), the template dimensions will mismatch by up to 1.5–2.0 pixels at the boundaries. If the lines in the diagram are thin (1 pixel), this scale discretization error can cause the edge alignment to exceed the 2-pixel tolerance, leading to false rejections at the coverage filtering stage.
