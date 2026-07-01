# Template Sweep Statistics Report

## Traceability
* **Timestamp**: 2026-06-17T00:32:16Z
* **Version**: Stage2_D3_v1
* **Manifest Version**: 1.0
* **Configuration**: `config/chamfer.yaml`

---

## 1. Sweep Operational Metrics
This report summarizes the operational statistics of the multi-scale template sweep engine.

* **Diagrams Evaluated**: 10
* **Templates Bank size**: 40 templates (10 scales, 4 rotations each)
* **Total Independent Sweeps**: 400 sweeps
* **Total Translation Coordinates Evaluated**: 259114360 positions
* **Total Pixel-Level Distance Comparisons**: 54912563372 comparisons
* **Total Run Time**: {TOTAL_RUNTIME:.3f} seconds

---

## 2. Detailed Operational Performance

| SLD Name | Templates Swept | Valid Positions Evaluated | Comparisons Made | Sweep Time (s) | Memory Peak (KB) | Candidates Extracted |
|---|---|---|---|---|---|---|
| SLD1 | 40 | 20927972 | 4420968595 | 0.644 | 2186.4 | 9316 |
| SLD10 | 40 | 54396552 | 11566254970 | 1.521 | 5483.4 | 62066 |
| SLD11 | 40 | 19453322 | 4119708639 | 0.584 | 1993.2 | 17027 |
| SLD12 | 40 | 2567362 | 520828437 | 0.095 | 324.6 | 2111 |
| SLD2 | 40 | 25422372 | 5389886019 | 0.727 | 2596.3 | 24450 |
| SLD3 | 40 | 23344022 | 4930840209 | 0.708 | 2442.0 | 47348 |
| SLD4 | 40 | 6776502 | 1419249935 | 0.249 | 737.1 | 2923 |
| SLD7 | 40 | 54636822 | 11614520795 | 1.510 | 5518.7 | 76750 |
| SLD8 | 40 | 17377212 | 3676276692 | 0.519 | 1793.7 | 16577 |
| SLD9 | 40 | 34212222 | 7254029081 | 0.994 | 3504.7 | 6284 |

---

## 3. Operational Integrity Verification
1. **Completeness Check**: Verified that all 40 template variants were swept across all 10 diagrams (total 400 sweeps), with no missing runs.
2. **Evaluated Position Alignment**: The number of evaluated positions matches the theoretical bounds $(W_D - W_T + 1) \times (H_D - H_T + 1)$ with 100% precision.
