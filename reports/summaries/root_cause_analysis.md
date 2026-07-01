# Root Cause Analysis

## Mathematical Cause of Degradation
The topological collapse at small scales is caused by the interaction between `cv2.INTER_AREA` downsampling and the subsequent binary thresholding (`cv2.THRESH_BINARY` with a threshold of 127).

1. **INTER_AREA Downsampling**: This method computes a pixel-area relation. When a thin edge line (1-2 pixels wide in the original) is scaled down by a factor of 4x to 6x (scale 0.15-0.20), the edge pixels become sub-pixel structures. The resulting grayscale values are heavily interpolated with the background.
2. **Binary Threshold Collapse**: Because the sub-pixel edges are blended with the white/black background, their resulting pixel intensity often falls below the 127 threshold. When `cv2.THRESH_BINARY` is applied, these faint grayscale lines are completely zeroed out (erased).
3. **Topological Disconnection**: This erasing selectively destroys the thinnest parts of the symbol first (often the vertical stem or the loops), causing the single connected symbol to shatter into isolated fragments.

## Visualization Bias vs True Collapse
The issue is **NOT** merely visual. It is a genuine topological collapse. The generated visual forensics show the templates cropped tightly to their own bounding boxes, confirming that the structures themselves have broken apart into disconnected dots and fragments.
