# Baseline Edge Template Generation Audit Report

## Traceability
- **Source Template**: `outputs/template/edges.png`
- **Generation Timestamp**: 2026-06-16T14:35:00Z
- **Scale Set Evaluated**: `[0.093, 0.100, 0.150, 0.200, 0.250, 0.300, 0.350, 0.400]`
- **Method Evaluated**: Method A (Baseline: Edge -> Resize -> Threshold)
- **Baseline Metrics Source**: Measured directly from `outputs/template/edges.png` at runtime

---

## 1. Executive Summary

This report documents the baseline performance and failure modes of the original Stage 2 template-generation pipeline (Method A). Method A applies spatial downsampling directly to the binary 1-pixel-thick Canny edge template, followed by a fixed global threshold of 127.

The audit confirms that Method A is completely non-functional across the lower half of the scale range:
* **Scale 0.093–0.200**: Complete topological collapse. The resulting templates contain exactly **0 edge pixels** (100% loss of shape information).
* **Scale 0.250**: Only 1 edge pixel survives (0.1% edge retention).
* **Scale 0.300–0.400**: High fragmentation. Although some edge pixels survive ($0.5\%$ to $2.4\%$ retention), the lines are completely fragmented into disconnected dots, with component counts diverging significantly from the baseline.

Method A is classified as **UNSUPPORTED** and requires immediate replacement.

---

## 2. Quantitative Benchmark Results

The following table records the measured metrics for Method A across all scales:

| Scale | Width | Height | Edges | Components (C) | Contours (K) | Continuity | Retention % | Stability | Density | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **0.093** | 15 | 10 | 0 | 0 | 0 | 0.000 | 0.0% | 0.00 | 0.0000 | **TOPOLOGY FAILURE** |
| **0.100** | 16 | 10 | 0 | 0 | 0 | 0.000 | 0.0% | 0.00 | 0.0000 | **TOPOLOGY FAILURE** |
| **0.150** | 24 | 15 | 0 | 0 | 0 | 0.000 | 0.0% | 0.00 | 0.0000 | **TOPOLOGY FAILURE** |
| **0.200** | 32 | 21 | 0 | 0 | 0 | 0.000 | 0.0% | 0.00 | 0.0000 | **TOPOLOGY FAILURE** |
| **0.250** | 40 | 26 | 1 | 1 | 1 | 1.000 | 0.1% | 0.12 | 1.0000 | **TOPOLOGY FAILURE** |
| **0.300** | 48 | 31 | 5 | 5 | 5 | 0.200 | 0.5% | 0.62 | 0.0075 | **PARTIALLY DEGRADED** |
| **0.350** | 56 | 36 | 10 | 9 | 9 | 0.200 | 1.1% | 1.12 | 0.0077 | **PARTIALLY DEGRADED** |
| **0.400** | 64 | 41 | 23 | 16 | 16 | 0.130 | 2.4% | 2.00 | 0.0105 | **TOPOLOGY FAILURE** |

---

## 3. Forensic Failure Mode Analysis

The topological collapse of Method A is caused by a mathematical conflict between downsampling and binarization:

1. **Sub-pixel Area Dilution**: The baseline edges are 1 pixel wide. When downsampling with `cv2.INTER_AREA`, the intensity of an edge pixel is averaged over a larger area (a factor of $4\times$ to $10\times$ depending on scale). 
2. **Threshold Deletion**: The resulting blurred grayscale edge pixels have intensities far below the global threshold of 127. When binarized, they are rounded down to 0, leaving empty canvases at scales $\le 0.20$.
3. **Severe Disconnection**: At larger scales ($0.30$ to $0.40$), only the pixels that happen to align perfectly with the target grid survive the 127 threshold. This leads to a dotted, highly fragmented appearance (e.g. 16 isolated single-pixel components at scale 0.40 instead of the 8 coherent baseline structures).

---

## 4. Downstream Risk Assessment

* **Chamfer Matching**: Stage 3 relies on computing distance transforms of these templates or matching them against query image edges. Empty templates yield no features, causing division-by-zero errors in normalization or flat-zero score surfaces.
* **PCA Verification**: Because features do not exist or are highly fragmented, bounding boxes cannot be estimated, leading to premature rejection of true detections.
