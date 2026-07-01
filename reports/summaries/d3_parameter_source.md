# Method D3 Parameter Source & Justification

## Traceability
- **Generation Timestamp**: 2026-06-16T23:45:00Z
- **Template Bank Version**: Stage2_D3_v1
- **Generation Method**: Method D3 (Coordinate Scaling + Anti-Aliased Rasterization)
- **Configuration Source**: `config/template_bank.yaml`
- **Manifest Version**: 1.0
- **Template Count**: 40

---

## 1. Hyperparameter Documentation & Rationale

This report provides the formal justification, mathematical origin, and experimental evidence for the hyperparameters defined in Method D3.

### 1.1 Subpixel Factor (F)
* **Parameter Value**: `8`
* **Purpose**: Sub-pixel coordinate scaling resolution.
* **Origin**: Discretization theory in computer graphics.
* **Evidence**: Stage 2.6 audit runs demonstrated that scaling coordinates directly with integer rounding at scale $0.15$ (where target image dimensions are $24 \times 15$) causes adjacent pixels to collide and collapse. By mapping coordinates to a high-resolution subpixel canvas ($192 \times 120$), we preserve high-precision floating-point coordinate relations before rasterization. A factor of $8\times$ balances subpixel accuracy with memory.
* **Expected Effect**: Reduces coordinate quantization error to less than $0.125$ target pixels.

### 1.2 Binarization Threshold
* **Parameter Value**: `25`
* **Purpose**: Binarization threshold for downsampled templates.
* **Origin**: Density-based thresholding (density $>10\%$).
* **Evidence**: The subpixel canvas has pixel values of 0 or 255. When resized using area interpolation to target scale, the output pixel value represents the fraction of its subpixel area that contains edges. A threshold of 25 corresponds to $\frac{25}{255} \approx 9.8\%$ area coverage. In Stage 2.6, this low threshold was shown to preserve continuity across all scales, whereas a standard threshold of 127 deleted valid boundaries.
* **Expected Effect**: Ensures that any target pixel containing even a single subpixel edge line segment is preserved, maintaining boundary connectivity.

### 1.3 Interpolation Method
* **Parameter Value**: `cv2.INTER_AREA`
* **Purpose**: Resizing interpolation strategy.
* **Origin**: Signal processing decimation standards.
* **Evidence**: Bilinear or bicubic interpolation on thin binary lines causes ringing artifacts and non-monotonic pixel distributions. Area interpolation averages pixel values over a grid cell, which naturally maps to the physical coverage ratio.
* **Expected Effect**: Prevents aliasing and moiré patterns in scaled images.

### 1.4 Rasterization Strategy
* **Parameter Value**: Coordinate-based `cv2.line` (thickness=1)
* **Purpose**: Line drawing on subpixel grid.
* **Origin**: Vector-to-raster conversion.
* **Evidence**: In Method D1, individual coordinates were scaled and plotted as single pixels, creating disconnected gaps (topology failure). By drawing connection lines between adjacent pixel coordinates, we guarantee a continuous path on the subpixel canvas, preventing gaps.
* **Expected Effect**: Ensures edge continuity is maintained at all scales, yielding $1.00$ continuity at lower bounds.
