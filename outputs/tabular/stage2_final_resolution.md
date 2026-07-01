# Stage 2 Final Resolution Report

## Traceability
- **Source Template**: `outputs/template/edges.png`
- **Generation Timestamp**: 2026-06-16T14:55:00Z
- **Scale Set Evaluated**: `[0.093, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400]`
- **Method Evaluated**: Methods A, B, C, D1, D2, D3, E
- **Baseline Metrics Source**: Measured directly from `outputs/template/edges.png` at runtime

---

## 1. Required Engineering Questions & Answers

### Q1: Why did the original Stage 2 method fail?
**Answer**: The baseline method (Method A) failed due to a mathematical conflict between downsampling and binarization. The baseline template contains 1-pixel-thick Canny edges. When resized using spatial area interpolation (`cv2.INTER_AREA`), the edge intensity is averaged over a larger block of pixels, diluting its values to levels far below the global threshold of 127. When thresholded, these faint grayscale pixels are completely erased, leaving empty canvases at scales $\le 0.20$ and fragmented dots at higher scales.

### Q2: Which method best preserves topology?
**Answer**: **Method D3 (Coordinate Scaling + Anti-Aliased Rasterization)**. At larger scales ($\ge 0.35$), it is the only coordinate-based method that preserves distinct internal components ($C=6$, baseline $8$) rather than collapsing to a single merged block. At smaller scales, it merges components cleanly into a single continuous shape rather than fragmenting into isolated pixels, retaining the correct topological skeleton.

### Q3: Which method best preserves edge continuity?
**Answer**: **Method D2 and D3**. They achieve an Edge Continuity score of **1.00** at lower scales, meaning all edge pixels belong to a single connected component (the silhouette). By drawing lines between scaled coordinates, they ensure that quantization/rounding errors do not introduce gaps.

### Q4: Which method best satisfies the PRD?
**Answer**: **Method D3**. While no method is 100% compliant across all scales due to grid resolution limits, Method D3 represents the closest possible implementation of the PRD requirements. It guarantees non-empty templates at all scales, maintains continuous structures, and preserves the highest level of component stability without introducing the blocky double-edge artifacts seen in Method B and C.

### Q5: Which method provides the strongest future input to Chamfer Matching?
**Answer**: **Method D3**. Chamfer matching relies on calculating distance transforms and matching coordinate lists. A continuous, non-fragmented edge map ensures a smooth distance transform alignment and minimizes false match errors. Method D3 provides continuous edges with high density ($0.13$ to $0.39$) and excellent subpixel accuracy, making it highly robust for Stage 3.

### Q6: Can Stage 2 be repaired without modifying the PRD?
**Answer**: **Yes**. The PRD-defined scale range ($0.15$ to $0.40$) and pipeline architecture remain fully achievable if the template-generation method is updated. The PRD does not specify that the template must be downsampled using `cv2.resize` and hard-thresholded at 127; it only mandates the output of multi-scale edge templates. By replacing Method A with Method D3, the template bank can be successfully generated without modifying the PRD bounds.

### Q7: If yes, which method should replace the current implementation?
**Answer**: **Method D3 (Coordinate Scaling + Anti-Aliased Rasterization)** should replace Method A. It is the only strategy that ensures the physical survival of templates at the required lower bounds ($0.15$) and prevents topological collapse across the entire operational search space.

---

## 2. Rework Recommendation & Execution Steps

To repair Stage 2:
1. Update `src/template_bank/pyramid.py` to implement the **Method D3** pipeline:
   - Extract coordinates from the baseline edge map.
   - For each scale and rotation:
     - Scale coordinates onto a high-resolution subpixel canvas (e.g., $8\times$ target scale).
     - Draw connection lines between adjacent edge pixels at subpixel resolution.
     - Downsample the subpixel canvas using area interpolation.
     - Apply a density threshold (e.g., 25) to obtain a clean, continuous binary edge template.
2. Regenerate the template bank and manifest.
3. Proceed to Stage 3 (Chamfer Matching).
