# Baseline Template Metrics Report

## Traceability
- **Source Template**: `outputs/template/edges.png`
- **Generation Timestamp**: 2026-06-16T09:01:17Z
- **Scale Set Evaluated**: N/A (Baseline)
- **Method Evaluated**: N/A (Baseline)
- **Baseline Metrics Source**: Measured directly from `outputs/template/edges.png` at runtime

---

## Measured Baseline Metrics

| Metric | Measured Value | Description |
|---|---|---|
| **Width** | 161 | Horizontal dimension of template image in pixels |
| **Height** | 103 | Vertical dimension of template image in pixels |
| **Edge Pixel Count** | 946 | Total number of non-zero edge pixels |
| **Connected Component Count (C)** | 8 | Count of 8-connected foreground structures (excluding background) |
| **Contour Count (K)** | 19 | Total count of contours extracted |
| **Bounding Box (x, y, w, h)** | (0, 2, 161, 101) | Tight bounding box enclosing all non-zero pixels |
| **Aspect Ratio (W/H)** | 1.5631 | Width divided by height |
| **Edge Density** | 0.0582 | Ratio of edge pixels to bounding box area |
| **Edge Continuity** | 0.2569 | Ratio of pixels in the largest connected component to total edge pixels |
