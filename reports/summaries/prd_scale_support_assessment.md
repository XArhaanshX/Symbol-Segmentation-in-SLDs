# PRD Scale Support Assessment

## Traceability
- **Source Template**: `outputs/template/edges.png`
- **Generation Timestamp**: 2026-06-16T14:40:00Z
- **Scale Set Evaluated**: `[0.093, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400]`
- **Method Evaluated**: Methods A, B, C, D1, D2, D3, E
- **Baseline Metrics Source**: Measured directly from `outputs/template/edges.png` at runtime

---

## 1. Compliance Audit Verdict

| Method | Can preserve topology throughout PRD range (0.15–0.40)? | Compliance Classification | Key Diagnostic Evidence |
|---|---|---|---|
| **Method A (Baseline)** | **NO** | **NON-COMPLIANT** | Empty templates (0 pixels) at scales $\le 0.20$. |
| **Method B (Binary First)** | **NO** | **NON-COMPLIANT** | Collapse to 2 components at scales $\le 0.20$. Severe fragmentation ($C=20$, target $8$) at scale 0.40. |
| **Method C (Grayscale First)** | **NO** | **NON-COMPLIANT** | Merges to 2 components at scales $\le 0.10$. Fragments ($C=19$, target $8$) at scale 0.40. |
| **Method D1 (Raw Coord)** | **NO** | **NON-COMPLIANT** | Complete structural merging ($C=1$ or $2$) at all scales. |
| **Method D2 (Reconstructed Coord)** | **NO** | **NON-COMPLIANT** | Complete structural merging ($C=1$ or $2$) at all scales. |
| **Method D3 (AA Subpixel)** | **NO** | **NON-COMPLIANT** | Merges to 1 or 2 components at scales $\le 0.30$. Preserved only at $\ge 0.35$. |
| **Method E (Grayscale Canny)** | **NO** | **NON-COMPLIANT** | Preserves topology at scale $0.25$ ($C=7$), but degrades at $0.15$ ($C=5$) and collapses to $C=2$ at $0.40$ due to auto-threshold instability. |

---

## 2. Rationale & Evidence for Non-Compliance

The primary blocker to achieving PRD compliance is a mathematical constraint of grid discretization, rather than a failure of the algorithms:

1. **The Sub-Pixel Gap Collision**:
   - The baseline MR symbol has 8 distinct components (outer circles, inner dots, caps, and lines) separated by small gaps of 1 to 2 pixels.
   - At the PRD minimum scale of $0.15$, the template is resized to $24 \times 15$ pixels.
   - The physical separation between the components shrinks to $1 \text{px} \times 0.15 = 0.15 \text{px}$ and $2 \text{px} \times 0.15 = 0.30 \text{px}$.
   - On a discrete pixel grid, a gap of $<0.5$ pixels cannot be represented. The pixels representing separate components must either overlap (causing them to merge, reducing $C$ to 1 or 2) or be deleted (causing them to disappear).
2. **The Fragmentation-vs-Merging Dilemma**:
   - Methods that try to prevent merging (like Method A and B at higher scales) end up splitting continuous lines, causing high fragmentation ($C \ge 16$).
   - Methods that guarantee connection (like Method D1 and D2) cause all components to merge into 1 or 2 structures.
   - Therefore, a template at scale $0.15$ cannot simultaneously maintain 8 disconnected components and continuous line boundaries.

---

## 3. Detailed Assessment by Method

* **Method A (Baseline)**: Completely non-functional. The fixed threshold deletes sub-pixel interpolation results, yielding empty images.
* **Method B (Binary First)**: Better than Method A, but Canny edge detection on a scaled, blocky binary mask results in high noise and line breakage at larger scales, while still failing below $0.20$.
* **Method C (Grayscale First)**: Shows the highest component stability at scale $0.15$ ($C=8$), but suffers from high fragmentation at scales $\ge 0.25$ ($C=18$ to $19$), rendering it unstable.
* **Method D (All Variants)**: Under D1 and D2, the rounding of coordinates to a small grid ($24\times15$) forces distinct shapes into adjacent pixels, causing complete merging. Variant D3 (anti-aliased subpixel) successfully preserves topology at scale $0.35$ and $0.40$, but collapses at lower scales.
* **Method E (Grayscale Canny)**: Represents a strong alternative because it operates on continuous gradients. However, local median-based thresholding is highly sensitive to image size, causing it to merge structures at scale $0.40$ ($C=2$) and fragment at $0.30$ ($C=3$).
