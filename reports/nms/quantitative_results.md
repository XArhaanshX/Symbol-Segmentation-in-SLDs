# NMS Diagnostic Evaluation — Quantitative Evaluation Results

## Monotonicity Validation Invariant
> [!IMPORTANT]
> **Invariant Check**: For greedy NMS, increasing the IoU threshold should never decrease the number of surviving detections. Equivalently, lower IoU thresholds should never produce more surviving detections than higher thresholds.
> **Validation Status**: SUCCESS (Monotonicity strictly preserved)

## Dual-Metric Evaluation Methodology
- **Metric A (Center-Distance Matching)**: Center distance ≤ `max(gt_w, gt_h)`. Evaluates localization accuracy.
- **Metric B (Bounding-Box IoU Matching)**: Bounding box IoU ≥ 0.5. Evaluates geometric localization quality.

## Expanded Detection Statistics across IoU Thresholds

### Overall Counts & Cluster Reduction
| IoU Threshold | Candidates Before | Candidates After | Total Suppressed | Suppression % | Duplicate Clusters Remaining | Mean Cluster Size | Duplicate Reduction % | Avg IoU Remaining |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 10000 | 2871 | 7129 | 71.3% | 0 | 0.0 | 100.0% | 0.0831 |
| 0.3 | 10000 | 3598 | 6402 | 64.0% | 0 | 0.0 | 100.0% | 0.1112 |
| 0.4 | 10000 | 4321 | 5679 | 56.8% | 738 | 2.7 | 50.2% | 0.1327 |
| 0.5 | 10000 | 5344 | 4656 | 46.6% | 1073 | 3.5 | 27.6% | 0.1568 |
| 0.6 | 10000 | 6230 | 3770 | 37.7% | 1228 | 4.0 | 17.1% | 0.1738 |
| 0.7 | 10000 | 7540 | 2460 | 24.6% | 1403 | 4.7 | 5.3% | 0.1915 |

### Metric A (Center-Distance Matching) Performance
| IoU Threshold | True Positives | False Positives | False Negatives | Precision | Recall | F1 Score | FP Removed | TP Removed |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 330 | 2541 | 205 | 0.1149 | 0.6168 | 0.1938 | 7112 | 17 |
| 0.3 | 337 | 3261 | 198 | 0.0937 | 0.6299 | 0.1631 | 6392 | 10 |
| 0.4 | 336 | 3985 | 199 | 0.0778 | 0.6280 | 0.1384 | 5668 | 11 |
| 0.5 | 339 | 5005 | 196 | 0.0634 | 0.6336 | 0.1153 | 4648 | 8 |
| 0.6 | 340 | 5890 | 195 | 0.0546 | 0.6355 | 0.1005 | 3763 | 7 |
| 0.7 | 343 | 7197 | 192 | 0.0455 | 0.6411 | 0.0850 | 2456 | 4 |

### Metric B (Bounding-Box IoU Matching) Performance
| IoU Threshold | True Positives | False Positives | False Negatives | Precision | Recall | F1 Score | FP Removed | TP Removed |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 6 | 2865 | 529 | 0.0021 | 0.0112 | 0.0035 | 7128 | 1 |
| 0.3 | 6 | 3592 | 529 | 0.0017 | 0.0112 | 0.0029 | 6401 | 1 |
| 0.4 | 7 | 4314 | 528 | 0.0016 | 0.0131 | 0.0029 | 5679 | 0 |
| 0.5 | 7 | 5337 | 528 | 0.0013 | 0.0131 | 0.0024 | 4656 | 0 |
| 0.6 | 7 | 6223 | 528 | 0.0011 | 0.0131 | 0.0021 | 3770 | 0 |
| 0.7 | 7 | 7533 | 528 | 0.0009 | 0.0131 | 0.0017 | 2460 | 0 |

### Top-K MR Enrichment (Metric A)
| IoU Threshold | Top-10 MR Count | Top-20 MR Count | Top-50 MR Count | Top-100 MR Count |
|---|---|---|---|---|
| 0.2 | 39 | 69 | 119 | 186 |
| 0.3 | 39 | 66 | 119 | 179 |
| 0.4 | 39 | 67 | 114 | 175 |
| 0.5 | 38 | 67 | 113 | 164 |
| 0.6 | 37 | 64 | 110 | 157 |
| 0.7 | 37 | 62 | 105 | 149 |

## Runtime Analysis (Patch 6)
- **Total Execution Time**: 6.59 seconds
- **Average Runtime per SLD**: 0.0730 seconds
- **Candidates Processed per Second**: 14602.9 cands/sec

| IoU Threshold | NMS Execution Time | Candidates / Sec |
|---|---|---|
| 0.2 | 0.50s | 20053.2 |
| 0.3 | 0.56s | 17817.3 |
| 0.4 | 0.65s | 15462.7 |
| 0.5 | 0.74s | 13480.3 |
| 0.6 | 0.89s | 11259.1 |
| 0.7 | 1.05s | 9544.9 |
