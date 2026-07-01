# Symbol-Specific Analysis Report: MR_Symbol.png

## Quantitative Metrics
- **Width:** 161
- **Height:** 103
- **Aspect Ratio:** 1.5631
- **Bounding Box:** x=0, y=2, w=161, h=101
- **Edge Pixel Count:** 956
- **Contour Count:** 3
- **Connected Component Count:** 1
- **Foreground Ratio:** 0.0997
- **Shape Complexity:** High (multi-contour, curved paths)
- **Symmetry:** Vertical symmetry axis present

## Qualitative Observations
- **Distinguishing geometric features:** Dual-semicircle lobes connected by a central horizontal line and bounded by vertical ticks. Very distinct from standard straight conductors.
- **Potential confusion sources:** Transformers, series inductors, or tightly curved buses may exhibit similar local curvature but lack the strict symmetry and topological termination of the MR symbol.
- **Rotation sensitivity:** The symbol is strictly directional. Horizontal versions (0/180 degrees) will have vastly different Chamfer signatures than vertical versions (90/270 degrees). Downstream matching must explicitly handle orientation.
- **Scale sensitivity:** Since stroke width is ~2px and internal gaps are small, severe downscaling (<0.5x) may cause topology merging, while upscaling (>2x) will broaden the distance transform basin dramatically.
