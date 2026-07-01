# NMS Diagnostic Evaluation — Baseline Candidate Statistics

This report establishes baseline geometric and spatial distribution statistics for candidate detections prior to Non-Maximum Suppression (NMS). All bounding box dimensions are strictly computed using detected scale metadata (`w = template_width × scale`).

## Per-SLD Baseline Statistics

| SLD | Total Candidates | Avg Candidate Area (px²) | Avg Overlap (IoU) | Max Overlap (IoU) | Duplicate Cluster Count | Avg Neighbor IoU |
|---|---|---|---|---|---|---|
| SLD1 | 1000 | 249.3 | 0.0061 | 0.9248 | 110 | 0.5705 |
| SLD10 | 1000 | 355.8 | 0.0049 | 0.9248 | 212 | 0.6297 |
| SLD11 | 1000 | 315.3 | 0.0097 | 0.9248 | 131 | 0.6368 |
| SLD12 | 1000 | 128.3 | 0.0027 | 0.8629 | 114 | 0.4245 |
| SLD2 | 1000 | 365.0 | 0.0083 | 1.0000 | 134 | 0.7063 |
| SLD3 | 1000 | 327.2 | 0.0053 | 0.9248 | 179 | 0.6201 |
| SLD4 | 1000 | 195.1 | 0.0028 | 1.0000 | 129 | 0.4919 |
| SLD7 | 1000 | 344.1 | 0.0023 | 0.9248 | 243 | 0.5679 |
| SLD8 | 1000 | 324.0 | 0.0110 | 0.9248 | 105 | 0.6924 |
| SLD9 | 1000 | 249.7 | 0.0121 | 0.9248 | 125 | 0.6402 |
