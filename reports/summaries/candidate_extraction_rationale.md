# Candidate Extraction Rationale Report

## Traceability
* **Timestamp**: 2026-06-17T00:32:16Z
* **Version**: Stage2_D3_v1
* **Manifest Version**: 1.0
* **Configuration**: `config/chamfer.yaml`
* **Local Minima Kernel Size**: 15

---

## 1. Definition of Candidate Proposal
A **Candidate Proposal** represents a single coordinate $(X, Y)$ in a target Single Line Diagram (SLD) where a specific template variant (defined by scale $s$ and rotation $\theta$) achieves a local geometric alignment. It is represented as a tuple:
$$\text{Proposal} = (\text{SLD Name}, \text{Template ID}, \text{Scale}, \text{Rotation}, X, Y, \text{Chamfer Score})$$

## 2. Why Local Minima Represent Candidate Hypotheses
In Chamfer matching, the score at any translation offset $(X, Y)$ is the mean Euclidean distance from the template's edge pixels to the nearest edge pixels in the diagram:
$$D_{\text{chamfer}}(T, I) = \frac{1}{|E_T|} \sum_{p \in E_T} DT_I(p + t)$$
A perfect geometric match corresponds to a local minimum of $0.0$ pixels. Minor scaling, rotation, or preprocessing variations shift the score, but the physical location of the symbol remains centered inside a **local basin of attraction** (a local minimum in the score field). 
Extracting the local minima allows us to pin down the coordinates of these basins, which represent the locations of best local geometric alignment.

## 3. Why Local Minima Are Not Filtering or Suppression
* **No Filtering**: We do not discard any local minima based on score thresholds or coverage ratios. Every local minimum basin, no matter how weak (high Chamfer score), is preserved.
* **No Suppression**: We do not merge overlapping candidate proposals across different scale/rotation variants. If multiple scales or orientations achieve a local minimum at nearby coordinates, all of these hypotheses are fully preserved. Suppression (specifically Spatial NMS) is deferred to Stage 5.
* **No Coverage Filtering**: We do not compute or filter by the fraction of covered template edges. This is deferred to Stage 4.

## 4. Alternative Methods Considered
1. **Top-K Response Extraction**:
   - *Method*: Retain the $K$ globally lowest Chamfer scores across the entire image.
   - *Rejection Rationale*: Top-K ignores spatial distribution. If a single region has a strong matching basin, all Top-K proposals might cluster within a few pixels of that same basin, completely failing to propose candidates in other parts of the diagram.
2. **Connected Valleys (Segmentation of Score Fields)**:
   - *Method*: Threshold the score map and extract the centroids of the connected regions.
   - *Rejection Rationale*: Requires choosing a score threshold, which constitutes premature candidate filtering.
3. **Regional Minima**:
   - *Method*: Find flat, connected regions of constant minimum values.
   - *Rejection Rationale*: Since diagrams consist of clean lines and smooth distance gradients, local minima are sharp and isolated, making simple local minima detection mathematically superior.

## 5. Expected Candidate Characteristics
The extracted proposals will contain:
1. **True Positives**: Low Chamfer scores (< 1.5 pixels) with template scales/rotations matching the symbols.
2. **False Positives**: Higher scores representing structural features in the diagram (e.g. T-junctions, corners, busbars) that happen to align partially with the template.
3. **Scale/Rotation Duplicates**: Multiple proposals at the same physical location representing different template scales/orientations.
All of these will be resolved deterministically in Stage 4 (Coverage Filtering) and Stage 5 (Non-Maximum Suppression).
