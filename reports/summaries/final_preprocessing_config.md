# Final Preprocessing Configuration Report

This authoritative document details the final preprocessing decisions made after executing Phase 1A (Dataset Audit), Phase 1B (Experiments), and evaluating the visual and quantitative results.

---

## Selected Blur Strategy

**Chosen Method**: Median Blur
**Parameters**: Kernel Size = 3

**Reason**: 
The dataset consists of high-contrast line drawings that exhibit discrete, isolated salt-and-pepper noise and compression artifacts rather than smooth Gaussian noise. 

**Evidence**: 
Visual inspection of the `blur_comparison` grids shows that a `3x3` Median filter aggressively eliminates single-pixel anomalies without smudging the sharp boundaries of the geometric strokes. The foreground structure of the MR symbol remains perfectly intact.

**Rejected Alternatives**:
- **No Blur**: Leaves isolated noise pixels which become spurious edges during Canny detection, generating false minima in the distance transform.
- **Gaussian Blur (k=3)**: Smudges and softens the sharp transitions of the binary lines, expanding the stroke width and making the edge localization less precise.

---

## Selected Thresholding Strategy

**Chosen Method**: Otsu Thresholding

**Reason**: 
The synthetic nature of single-line diagrams ensures a strongly bimodal pixel intensity distribution (as confirmed by the Histogram Analysis). Otsu's method automatically calculates the optimal global threshold to separate these modes.

**Evidence**: 
The `threshold_comparison` grid demonstrates that Otsu correctly isolates the black conductors from the white background across varying file encodings without requiring manual tuning. The connected component count remains low, indicating solid shapes.

**Rejected Alternatives**:
- **Global Threshold (127)**: Fails to adapt if lighting, anti-aliasing, or encoding alters the background intensity.
- **Adaptive Thresholding (Gaussian/Mean)**: The local block-based nature introduces severe noise halos around high-contrast edges and artifacts in large empty white spaces, severely degrading the Chamfer matching basin.
- **Sauvola Thresholding**: While robust, it is computationally heavier and requires tuning local window sizes and constants. It offers no practical advantage over Otsu on this specific bimodal dataset.

---

## Selected Edge Detection Strategy

**Chosen Method**: Canny Edge Detection
**Parameters**: Automatic Median-Based Thresholds (`lower = 0.67 * median_intensity`, `upper = 1.33 * median_intensity`)

**Reason**: 
Chamfer matching relies heavily on precise, thin contours to establish narrow distance transform basins. Canny's non-maximum suppression guarantees edges that are exactly 1 pixel wide.

**Evidence**: 
Visual inspection of the `edge_comparison` outputs confirms that Canny extracts the skeletal boundary of the MR symbol perfectly. The continuity of the dual-semicircle lobes is maintained through the hysteresis thresholds.

**Rejected Alternatives**:
- **Sobel / Scharr**: Produces thick, blurry gradient magnitudes that require secondary thresholding and thinning. The resulting edges are too wide for precise Chamfer alignment.
- **Morphological Gradient**: Computes `dilation - erosion`, effectively outlining the stroke. While deterministic, it treats the inner and outer boundaries identically and can result in "double edges" for thicker strokes, confusing the distance transform.

---

## Selected Parameters Configuration

- **blur_kernel**: `3`
- **blur_type**: `median`
- **threshold_method**: `otsu`
- **edge_detector**: `canny`
- **canny_auto**: `true`
- **canny_sigma**: `0.33` (used for median deviation bounds)
- **save_intermediate**: `true`

---

## Expected Benefits

By utilizing Median Blur, Otsu Thresholding, and Auto-Canny Edge Detection, the representation strips away all non-geometric noise (colors, compression artifacts, text anti-aliasing) while maintaining the exact topological shape of the MR Symbol. 

The resulting edge map is perfectly thin (1px), which generates the sharpest, steepest possible Distance Transform basins. This representation is highly optimal for downstream multi-scale Chamfer geometric matching.
