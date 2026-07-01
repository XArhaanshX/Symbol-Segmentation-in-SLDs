# Distance Transform Validation Report

## Traceability
* **Timestamp**: 2026-06-17T00:29:46Z
* **Version**: Stage2_D3_v1
* **Manifest Version**: 1.0
* **Configuration**: `config/chamfer.yaml`
* **Local Minima Kernel Size**: 15
* **Score Map Storage Format**: npy

---

## Executive Summary
This report validates the Euclidean Distance Transforms (DT) computed for the target diagrams under Stage 3a. Distance transforms are floating-point representations where each pixel represents the spatial Euclidean distance to the nearest edge pixel in the binarized diagram.

**Validation Result**: PASS

---

## Detailed Measurements

| SLD Name | Width | Height | Min Distance | Max Distance | Mean Distance | NaN Present | Inf Present | Transform Status |
|---|---|---|---|---|---|---|---|---|
| SLD10 | 1581 | 915 | 0.0000 | 242.4775 | 52.2424 | False | False | VALID |
| SLD11 | 769 | 698 | 0.0000 | 198.9067 | 40.0274 | False | False | VALID |
| SLD12 | 871 | 112 | 0.0000 | 66.9690 | 19.3424 | False | False | VALID |
| SLD1 | 1544 | 382 | 0.0000 | 249.1302 | 64.8740 | False | False | VALID |
| SLD2 | 1024 | 678 | 0.0000 | 231.7675 | 37.8348 | False | False | VALID |
| SLD3 | 1789 | 368 | 0.0000 | 177.5612 | 36.6905 | False | False | VALID |
| SLD4 | 806 | 255 | 0.0000 | 138.4263 | 29.4833 | False | False | VALID |
| SLD7 | 1778 | 819 | 0.0000 | 135.6636 | 33.0107 | False | False | VALID |
| SLD8 | 901 | 537 | 0.0000 | 212.8760 | 50.8654 | False | False | VALID |
| SLD9 | 1700 | 549 | 0.0000 | 419.1039 | 108.7224 | False | False | VALID |

---

## Verification Assertions
1. **Edge Anchoring Check**: Min Distance must be exactly `0.0` or close to `0.0` at the locations of the diagram edges.
2. **Smooth Gradient Check**: Mean distance values should reflect the overall density of the edge map (sparsely populated maps will have higher mean distances).
3. **No NaNs/Infs**: Distance values must be real finite floating-point numbers.
