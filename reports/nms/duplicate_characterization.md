# NMS Diagnostic Evaluation — Duplicate Characterization Analysis

## Purpose
This diagnostic stage quantifies whether duplicate overlapping detections are actually present before applying any suppression. It establishes objective evidence to determine whether duplicate detections represent a genuine failure mode in the localization pipeline prior to evaluating NMS.

## Per-SLD Duplicate Characterization Summary

| SLD | Duplicate Cluster Count | Avg Overlapping Neighbors | Mean Cluster Size | Max Cluster Size | Max Overlap Observed | Avg Neighbor IoU |
|---|---|---|---|---|---|---|
| SLD1 | 110 | 16.09 | 8.5 | 101 | 0.9248 | 0.5705 |
| SLD10 | 212 | 10.77 | 4.3 | 205 | 0.9248 | 0.6297 |
| SLD11 | 131 | 21.36 | 7.2 | 117 | 0.9248 | 0.6368 |
| SLD12 | 114 | 7.99 | 7.0 | 45 | 0.8629 | 0.4245 |
| SLD2 | 134 | 18.05 | 7.1 | 262 | 1.0000 | 0.7063 |
| SLD3 | 179 | 10.95 | 5.2 | 70 | 0.9248 | 0.6201 |
| SLD4 | 129 | 8.62 | 7.1 | 34 | 1.0000 | 0.4919 |
| SLD7 | 243 | 5.32 | 3.6 | 42 | 0.9248 | 0.5679 |
| SLD8 | 105 | 23.97 | 9.1 | 139 | 0.9248 | 0.6924 |
| SLD9 | 125 | 31.75 | 7.5 | 209 | 0.9248 | 0.6402 |

## Dataset-Wide Aggregates
- **Total Duplicate Clusters**: 1482
- **Max Cluster Size Observed**: 262
- **Global Mean Overlap (non-zero)**: 0.2548
- **Global Avg Neighbor IoU**: 0.5980

## Diagnostic Verdict
The high concentration of duplicate clusters and substantial overlapping neighbor counts confirm that redundant detections are a prevalent and genuine failure mode across all SLDs. Evaluating Non-Maximum Suppression (NMS) is structurally justified.
