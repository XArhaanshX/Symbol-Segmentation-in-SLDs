# Stage 3 Candidate Generation Report

## Traceability
* **Timestamp**: 2026-06-17T00:32:16Z
* **Version**: Stage2_D3_v1
* **Manifest Version**: 1.0
* **Configuration**: `config/chamfer.yaml`

---

## 1. Candidate Generation Overview
Stage 3 converts the dense edge distance fields of the SLDs into discrete candidate proposals. 
This is achieved by precomputing Euclidean Distance Transforms for the diagrams, sliding each Method D3 template variant over the distance fields using 2D cross-correlation, saving the dense float32 score fields, and extracting local minima.

* **Input Data**: 10 Preprocessed SLD diagrams (`edges.png`)
* **Active Template Bank**: `Stage2_D3_v1` (40 scale/rotation variants)
* **Outputs Generated**:
  - Distance Transforms: `outputs/distance_transforms/SLD*_dt.tiff`
  - Chamfer Score Maps: `outputs/score_maps/SLD*_T_*.npy`
  - Raw Candidate Proposals: `outputs/candidates/raw_candidates.csv`
  - Ranked Candidate Proposals: `outputs/candidates/ranked_candidates.csv`

---

## 2. Methodology & Math
1. **Precomputed Distance Fields**: Precomputing Euclidean DT reduces distance lookup to $\mathcal{O}(1)$ per edge pixel during templates sweeping.
2. **Fast Chamfer Matching**: Using `cv2.filter2D` allows computing the sum of distance transform values under the template's active edge pixels in parallel across the entire image within sub-milliseconds.
3. **Local Minima Extraction**: We locate the exact grid coordinates of the local minimum basins of attraction. To prevent flat empty diagram plateaus from proposing candidates, we check that the local minimum is strictly lower than the local maximum in a $15 \times 15$ neighborhood.

---

## 3. Observations & Key Findings
1. **Hypothesis Retention**: A total of **264852 proposals** were extracted and ranked. Since no thresholding or filtering was applied, all plausible spatial hypotheses for all template scales and orientations are preserved.
2. **True Detections**: Original symbol locations are successfully captured as candidates with very low Chamfer scores.
3. **Noise Handling**: The output contains abundant false positives (text blocks, busbar corners, parallel line structures) and overlapping duplicates. These are expected and will be handled by Stage 4 (Coverage Filtering) and Stage 5 (Non-Maximum Suppression).
