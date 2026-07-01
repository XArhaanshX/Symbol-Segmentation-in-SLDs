# Edge Detector Comparison Experiment

## MR_Symbol

![MR_Symbol Edge Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/MR_Symbol_edge_comp.png)

## SLD4

![SLD4 Edge Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD4_edge_comp.png)

## SLD11

![SLD11 Edge Comparison](file:///C:/Users/arhaa/OneDrive/Symbol Segmentor/reports/visual_validation/SLD11_edge_comp.png)

## Observations & Recommendation
- **Canny**: Provides incredibly thin (1-pixel width), connected contours. Hysteresis thresholding helps maintain continuity in dashed lines.
- **Sobel / Scharr**: The gradients are thick and require secondary thresholding and thinning to be useful for Chamfer matching, otherwise the distance transforms are too broad.
- **Morphological Gradient**: Provides deterministic boundaries exactly 1 pixel thick around binary blobs, but treats inner and outer boundaries identically, sometimes creating "double lines" depending on stroke width.

**Selected Edge Detection Strategy**: Canny Edge Detection (Auto-Median Threshold).
**Reason**: It yields thin, highly localized edges. The non-maximum suppression intrinsic to Canny guarantees 1px wide responses, which generates the steepest, cleanest distance transform basins for geometric matching.
