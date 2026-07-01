# Method D3 Parameter Freeze Report

## Traceability
- **Generation Timestamp**: 2026-06-16T23:44:00Z
- **Template Bank Version**: Stage2_D3_v1
- **Generation Method**: Method D3 (Coordinate Scaling + Anti-Aliased Rasterization)
- **Configuration Source**: `config/template_bank.yaml`
- **Manifest Version**: 1.0
- **Template Count**: 40

---

## 1. Frozen Parameters Specification

The following parameter values are frozen for Stage 2.7 to ensure exact reproduction of the audited Method D3 benchmark results:

| Parameter Name | Frozen Value | Source | Stage 2.6 Evidence Reference | Reason for Freezing |
|---|---|---|---|---|
| **Subpixel Factor (F)** | `8` | Stage 2.6 Audit | `benchmark_edge_generation.py:129` | Determines the resolution of the subpixel grid (canvas width/height = target width/height $\times$ 8). Higher factor increases subpixel coordinate accuracy but raises memory footprint. Value of 8 is the audited choice. |
| **Binarization Threshold** | `25` | Stage 2.6 Audit | `benchmark_edge_generation.py:144` | Set to 25 (equivalent to a density of $>10\%$ inside each downsampled pixel block). Lower values retain faint edge features; higher values suppress noise. Audited value of 25 provides optimal continuity. |
| **Interpolation Method** | `cv2.INTER_AREA` | Stage 2.6 Audit | `benchmark_edge_generation.py:141` | OpenCV area-based interpolation. It computes pixel area relation, which is mathematically ideal for decimation/downsampling. |
| **Rasterization Strategy** | Coordinate-based `cv2.line` (thickness=1) | Stage 2.6 Audit | `benchmark_edge_generation.py:134-139` | Coordinates of adjacent pixel pairs are connected using lines on the subpixel grid. This guarantees continuous paths and prevents fragmentation from integer rounding. |

---

## 2. Reproduction Agreement

By freezing these parameters, we guarantee that Stage 2.7 acts purely as a controlled execution of the Stage 2.6 design decision, preventing unverified modifications or parameter drift.
