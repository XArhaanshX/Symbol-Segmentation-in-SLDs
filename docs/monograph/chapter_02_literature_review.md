# Chapter 2 — Literature Review

## 2.1 Template Matching in Computer Vision

Template matching is one of the oldest problems in computer vision, dating to the 1970s when correlation-based methods were first applied to industrial inspection tasks. The fundamental operation — sliding a reference template across a target image and computing a similarity measure at each position — remains conceptually unchanged, though the choice of similarity metric, the handling of geometric transformations, and the integration of domain knowledge have evolved substantially.

### 2.1.1 Pixel-Domain Methods

**Normalized Cross-Correlation (NCC)** computes the Pearson correlation coefficient between template and image pixel intensities at each sliding-window position. NCC is invariant to linear brightness and contrast changes, making it suitable for natural images with photometric variation. OpenCV implements this as `cv2.matchTemplate()` with the `TM_CCOEFF_NORMED` flag.

However, NCC operates in the pixel domain, making it fundamentally sensitive to contextual variations. In engineering line drawings, the local pixel context around a symbol is highly variable — different neighboring symbols, different text labels, different bus orientations all alter the pixel content within the matching window. This context sensitivity was identified in the PRD (Section 4.2) as a primary limitation for this domain.

**Sum of Squared Differences (SSD)** and its normalized variant compute the L2 distance between template and image patches. SSD is computationally efficient but lacks robustness to any intensity transformation and is highly sensitive to partial occlusion and contextual clutter.

### 2.1.2 Edge-Domain Methods

**Chamfer Matching** (Barrow et al., 1977; Borgefors, 1988) operates in the edge domain rather than the pixel domain. The algorithm:

1. Extracts edge maps from both template and target image
2. Precomputes the Euclidean Distance Transform (DT) of the target edge map
3. For each sliding-window position, sums the DT values at template edge pixel locations
4. The mean of these values constitutes the Chamfer distance — the average distance from each template edge pixel to its nearest target edge pixel

The mathematical formulation is:

$$d_{Chamfer}(T, I; t_x, t_y) = \frac{1}{|E_T|} \sum_{(e_x, e_y) \in E_T} DT_I(t_y + e_y, t_x + e_x)$$

where $E_T$ is the set of template edge pixels, $DT_I$ is the distance transform of the target edge map, and $(t_x, t_y)$ is the translation offset.

Chamfer matching has several properties that make it well-suited for line-drawing analysis:
- **Edge-domain operation**: Naturally suited to binary line drawings where geometric structure, not pixel intensity, carries the information
- **Robustness to minor deformation**: The distance transform provides a smooth scoring landscape, tolerating small geometric variations
- **Computational efficiency**: The DT precomputation is O(W×H) and enables O(1) distance lookup per edge pixel
- **Determinism**: No stochastic components; identical inputs produce identical outputs

**Hausdorff Distance** measures the maximum (rather than mean) distance between edge sets. While more sensitive to outlier edges, it provides stronger guarantees that every part of the template has a corresponding edge in the target. The max operator makes it highly sensitive to spurious edges from bus conductors passing through the matching window — a critical weakness for this domain.

### 2.1.3 Multi-Scale Template Matching

When the template and target symbols differ in scale, single-scale matching fails entirely. Multi-scale approaches construct a **scale pyramid** of template variants and search across all scales simultaneously. The computational cost scales linearly with the number of scale levels.

For this project, the template (161×103 pixels) is 4–6× larger than diagram symbols (~25–40 pixels). The PRD specifies a scale range of [0.15, 0.40] with 10 linearly-spaced levels, producing templates from approximately 24×15 to 64×41 pixels.

### 2.1.4 Coverage Ratio as a Complementary Signal

The **coverage ratio** (also called the match ratio or proximity ratio) measures the fraction of template edge pixels that fall within a distance threshold τ of a target edge pixel:

$$\text{Coverage}(T, I; t_x, t_y, \tau) = \frac{1}{|E_T|} \sum_{(e_x, e_y) \in E_T} \mathbb{1}[DT_I(t_y + e_y, t_x + e_x) \leq \tau]$$

This metric is related to the Chamfer distance but provides a bounded [0, 1] signal that reflects the proportion of template edges finding nearby target edges, rather than the average distance. It was adopted as a complementary filtering criterion with τ=2.0 pixels and a minimum threshold of 0.65.

## 2.2 Shape Matching and Structural Analysis

### 2.2.1 Shape Context Descriptors

Belongie et al. (2002) introduced shape context as a rich descriptor for point-based shape matching. For each contour point, a log-polar histogram of the relative positions of all other contour points is computed. Shape matching then reduces to finding the optimal correspondence between point sets that minimizes the cost of descriptor dissimilarity plus a deformation term.

Shape context requires **isolated contours** — clean, closed boundaries around the target shape. In SLDs, MR symbols are topologically embedded in bus conductors (the vertical stem connects directly to the horizontal bus), making contour isolation impossible without prior segmentation. This fundamental limitation was identified during the PRD architecture evaluation and confirmed empirically during Stages 2–2.75.

### 2.2.2 Skeleton-Based Matching

Medial axis transforms (Blum, 1967) reduce a shape to its topological skeleton, enabling structure-preserving comparison. Skeleton matching methods compute branch counts, endpoint locations, junction positions, and branch lengths to characterize shapes. This project extensively used skeletonization (via `skimage.morphology.skeletonize`) as part of the Stage 5.8 structural feature extraction pipeline, computing Branch_Point_Count, Endpoint_Count, Average_Branch_Length, and related features.

The skeleton-based features showed moderate discriminative power (AUC=0.757 for Endpoint_Count vs Dominant FP) but were ultimately classified as partially redundant with existing signals (Pearson r=0.31 with scale).

### 2.2.3 Connected Component Analysis

Connected component analysis (CCA) decomposes a binary image into spatially disjoint regions. If a target symbol existed as an isolated connected component, CCA would provide trivial localization — simply enumerate all components and match against the template.

This project empirically invalidated CCA for MR symbol localization across Stages 2, 2.5, and 2.75. The MR symbol does NOT emerge as an isolated connected component because:
- It is **topologically connected** to the bus conductor via its vertical stem
- Wire suppression (morphological opening with a horizontal kernel) removes horizontal conductors but does not sever the vertical stem connection
- Morphological closing experiments recovered coil continuity but did not enable component isolation
- Even with relaxed filtering thresholds (allowing 4× the template area), zero additional MR candidates were recovered

This negative result is significant because it definitively eliminates the simplest possible localization strategy for this specific symbol-diagram configuration.

### 2.2.4 Graph-Based Methods

Graph Edit Distance (GED) represents shapes as attributed graphs (nodes = junctions/endpoints, edges = branches) and measures similarity as the minimum cost of edit operations (node/edge insertion, deletion, substitution) to transform one graph into another. GED is NP-hard in general but approximable for small graphs.

This project computed graph-based features during Stage 5.8 (using `networkx`), including Node_Count_Difference, Edge_Count_Difference, Graph_Density_Difference, and approximate GED. The graph features showed moderate separability (AUC=0.681 for Junction_Similarity vs Dominant FP) but were classified as redundant with existing structural verification scores.

The full GED computation was rejected as the primary matching method due to computational intractability at the scale required (hundreds of thousands of candidate evaluations) and over-engineering for the MR symbol's relatively simple topology.

## 2.3 One-Shot and Few-Shot Detection

### 2.3.1 Siamese Networks

Siamese networks (Koch et al., 2015) learn a metric embedding space where similar inputs are mapped close together. For one-shot detection, a Siamese network compares a query template against candidate regions to produce a similarity score.

While architecturally compatible with the one-shot constraint, Siamese networks require:
- A **training distribution** of positive and negative pairs from many classes to learn the embedding
- Pre-training on a domain-relevant corpus (Omniglot, miniImageNet, etc.)
- GPU infrastructure for efficient training and inference

For engineering line drawings, no such training corpus exists. Pre-training on natural image pairs would transfer statistics irrelevant to binary line drawings. The domain gap between natural photographs and engineering schematics makes transfer learning fundamentally unsuitable.

### 2.3.2 Few-Shot Object Detection (YOLO, Faster R-CNN, DETR)

Modern supervised object detectors require 1,000–50,000+ annotated training images to learn discriminative features. This project has zero annotated bounding boxes, one template image (not a training image), and 10 target images (not a training set). The data requirements are fundamentally unmet.

Even with aggressive augmentation of the single template, supervised detectors cannot learn:
- Background context statistics (what is NOT the symbol)
- Hard negative examples (G/B boxes that look similar but are not MR symbols)
- Scale/aspect ratio distributions from real scene-level examples

Data augmentation of a single isolated template produces artificial training examples that do not reflect the actual in-context appearance of the symbol embedded within bus structures. This was identified as a "hard reject" (0/10 suitability) in the PRD architecture evaluation.

### 2.3.3 Vision Transformers (ViT, DINOv2)

Self-supervised vision transformers learn patch-level representations through attention mechanisms over large-scale image corpora. DINOv2's self-supervised features could theoretically provide good representations without labeled data, but the features are learned from natural images (ImageNet-scale), and engineering line drawings lie far outside this distribution. Fine-tuning requires labeled data that is unavailable.

## 2.4 Feature Detection and Description

### 2.4.1 Keypoint Detectors (SIFT, SURF, ORB, AKAZE)

Classical keypoint detectors are designed for natural images with rich texture gradients. Engineering line drawings consist of thin lines and arcs that produce:
- Very few stable keypoints (0–5 per symbol)
- High positional instability in the scale-space pyramid
- Non-distinctive descriptors at junction points (shared across symbol types)

The fundamental domain mismatch between textured natural images and binary line drawings renders all classical keypoint-based methods unsuitable as primary localization mechanisms. This was confirmed empirically by the PRD team and assigned suitability scores of 1–3/10.

### 2.4.2 Histogram of Oriented Gradients (HOG)

HOG descriptors capture local gradient orientation statistics in a fixed-size window. While HOG can characterize edge structure, it discards spatial arrangement — two regions with the same gradient histogram but different spatial layouts would score identically. For MR symbol discrimination, spatial structure is the critical differentiator (the specific arrangement of semicircular lobes, base bar, and vertical stem).

## 2.5 PCA-Based Appearance Verification

Principal Component Analysis (PCA) constructs a linear subspace from a collection of appearance examples. For one-shot symbol verification, PCA operates as follows:

1. Generate augmented views of the single template (scale, rotation, morphological variations)
2. Flatten each view into a high-dimensional vector
3. Center and compute principal components → defines the "symbol appearance manifold"
4. For each candidate detection, extract and flatten the image patch
5. Project into the PCA subspace and reconstruct
6. Compute reconstruction error: high error = poor manifold membership = likely not the target symbol

PCA verification provides an **orthogonal semantic signal** to Chamfer matching: Chamfer measures geometric proximity of edges, while PCA measures appearance manifold membership. The score fusion formula documented in the PRD is:

$$S_{fused} = w_c \cdot \exp(-\alpha \cdot d_{chamfer}) + w_p \cdot \exp(-RE / \tau)$$

with empirically calibrated parameters α=2.0, w_c=0.7, w_p=0.3.

## 2.6 Engineering Drawing Analysis

### 2.6.1 Document Image Analysis for Technical Drawings

The analysis of engineering drawings has a long history in document image analysis, with early work focused on vectorization (converting raster images to vector graphics) and text/graphics separation. Key challenges include:
- Line-drawing-specific preprocessing (binarization, noise removal, wire suppression)
- Symbol isolation from connected topologies (the fundamental barrier for CCA)
- Multi-scale symbol recognition across different drawing conventions
- Text-symbol disambiguation in dense regions

### 2.6.2 Single Line Diagram (SLD) Analysis

SLDs present unique challenges compared to other engineering drawing types:
- Symbols are connected to bus conductors, preventing isolated extraction
- Symbol density varies dramatically (6–36 per diagram)
- Multiple symbol types share geometric sub-primitives (boxes, circles, zigzags)
- Scale variation within a single drawing is minimal, but scale mismatch between template and diagram is extreme (4–6×)

The combination of topological embedding, geometric ambiguity, and extreme scale mismatch makes SLD symbol localization a challenging instance of the general engineering-drawing-analysis problem.

## 2.7 Distance Transforms

The Euclidean Distance Transform (EDT) computes, for every pixel in a binary image, the Euclidean distance to the nearest foreground (or background) pixel. The Felzenszwalb-Huttenlocher (2012) algorithm computes the exact EDT in O(n) time (linear in the number of pixels), enabling efficient precomputation for Chamfer matching.

Properties critical to this project:
- DT(x,y) = 0 at edge pixels and increases smoothly away from edges
- Creates a smooth scoring landscape for Chamfer matching (no discrete jumps)
- Enables O(1) distance lookup per template edge pixel during sliding-window search
- OpenCV implementation (`cv2.distanceTransform`) uses DIST_L2 with mask size 5 for Euclidean approximation

## 2.8 Non-Maximum Suppression (NMS)

Non-Maximum Suppression is a standard post-processing step in object detection that removes redundant overlapping detections. The greedy NMS algorithm:

1. Sort detections by confidence score (descending)
2. Select the highest-scored detection
3. Remove all remaining detections with IoU > threshold against the selected detection
4. Repeat until no detections remain

This project extensively evaluated NMS across 6 IoU thresholds (0.20–0.70) during the NMS Diagnostic Evaluation (Stage 5.12), characterizing duplicate clusters, suppression rates, and true positive preservation. The evaluation established that NMS is structurally justified (duplicate clusters are prevalent) but operates as a spatial filter rather than a semantic discriminator.

## 2.9 Evaluation Metrics for Object Detection

### 2.9.1 Localization Metrics

- **Intersection over Union (IoU)**: Measures geometric overlap between predicted and ground truth bounding boxes. Standard threshold: IoU ≥ 0.50 for a true positive.
- **Center-Distance Matching**: An alternative matching criterion where a detection is a true positive if its center falls within a distance threshold of the ground truth center. This project used max(gt_w, gt_h) as the threshold — a localization-appropriate criterion for symbols where precise bounding box alignment is less critical than center localization.

### 2.9.2 Ranking Metrics

- **Mean Reciprocal Rank (MRR)**: The mean of 1/rank of the first correct detection per SLD. Higher MRR indicates that true symbols appear earlier in the ranked list.
- **Recall@K**: The fraction of true symbols appearing within the top-K candidates. Recall@10, @20, @50, @100, and @500 provide a retrieval-oriented evaluation of ranking quality.
- **Median MR Rank**: The median rank position of true MR symbols across all SLDs. Lower is better.

### 2.9.3 Signal Enrichment Metrics

- **Candidate Reduction %**: The percentage decrease in candidate count from baseline to post-filtering. Measures computational efficiency gain.
- **MR Density**: The fraction of candidates that are true MR symbols. Higher density indicates better signal-to-noise ratio.
- **MR Density Gain**: The multiplicative improvement in MR Density relative to baseline. A gain of 10× means the filtered set has 10× more true positives per candidate.

---

*Forensic Source References:*
- *PRD Sections 4.1–4.23, 5.1–5.3: Architecture survey and rejection justifications*
- *`exploration/archived/misc/PRD_Symbol_Localization.md`, lines 200–1000*
- *Stage 5.8 structural feature extraction: `exploration/archived/scripts/stage5_8_structural_discovery.py`*
- *NMS diagnostic evaluation: `src/exploration/nms_diagnostic_evaluation.py`*
- *Unified pipeline benchmark: `src/exploration/unified_pipeline_benchmark.py`*
