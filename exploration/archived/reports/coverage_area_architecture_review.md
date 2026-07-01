# Stage 4 Architecture Review

<!-- Traceability Header -->
- **Generation Time**: 2026-06-17 01:56:45
- **Template Bank Version**: Stage2_D3_v1
- **Candidate Dataset Source**: outputs/candidates/ranked_candidates.csv
- **Coverage Metrics Source**: reports/coverage_metrics_dataset.csv
- **Structural Metrics Source**: reports/structural_metrics_dataset.csv
- **Manifest Version**: outputs/template_bank/template_bank_manifest.csv
- **Stage 3.5 Feasibility Report**: 1.0.0
- **Investigation Type**: Diagnostic Only
<!-- End Traceability Header -->



## 1. Why did Coverage Filtering fail?
Coverage Filtering failed because it fundamentally assumed that a higher coverage ratio directly corresponds to higher symbol likelihood. The empirical evidence demonstrates that small-scale false positives (Text and Conductors) naturally achieve near-perfect coverage ratios due to dense diagram edge maps, resulting in an inverted separation where false positives outscore True Symbols.

## 2. Is failure caused by scale bias, edge count bias, or fundamental signal limitations?
The failure is caused primarily by **Scale Bias**. The edge map density acts as a confounding variable that mathematically favors smaller templates with fewer edge pixels. It is a fundamental signal limitation when applied as an absolute global threshold across multiple scales.

## 3. Can normalization rescue Coverage?
Simulation indicates that normalization (e.g. Coverage $\times$ Scale or Coverage $\times$ TemplateArea) significantly shifts the distributions and partially corrects the bias. However, no single normalization completely eliminates the overlap between True Symbols and complex Conductors without strict calibration.

## 4. Does any measured signal outperform Coverage?
Yes. Multiple structural metrics (e.g. Connected Component Count Difference, Bounding Box IoU) and normalized coverage scores strongly outperform raw Coverage, which had a negative/inverted ROC-AUC relative to True Symbols.

## 5. Do structural descriptors provide stronger discrimination?
Yes. Structural features extracted directly from the candidate crops demonstrate an orthogonal discriminative signal that does not suffer from the same mathematical coupling as Chamfer and Coverage. 

## 6. Is Stage 4 salvageable?
Stage 4 is salvageable only if the "Absolute Global Coverage Threshold" paradigm is entirely abandoned. It must be repurposed into a scale-normalized rescoring stage or an adaptive bounding filter.

## 7. Should Stage 4 remain unchanged?
**No.** Leaving Stage 4 unchanged will result in the total suppression of True Symbols and 0% recall.

## 8. Should Stage 4 be redesigned?
**Yes.** Based on diagnostic evidence, Stage 4 must be redesigned to either use scale-normalized scoring, or it should be reduced in scope to a very relaxed bounds check.

## 9. Should Stage 5 verification move earlier?
Moving Stage 5 (Structural Verification/PCA) earlier or relying heavily upon it is strongly supported by the evidence. Structural descriptors have demonstrated superior discriminative capacity and independence from Chamfer matching artifacts.

## 10. What is the most evidence-supported path forward?
The evidence supports redesigning the architecture to:
1. **Redesign Stage 4**: Replace absolute coverage filtering with Scale-Normalized Scoring.
2. **Promote Stage 5**: Implement Structural/Layout Verification as the primary false-positive suppression engine.
