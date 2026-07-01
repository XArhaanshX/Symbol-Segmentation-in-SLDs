# NMS Diagnostic Evaluation — Architectural Verdict

## Q1. How many duplicate detections existed?
- **Measured Value**: 1482 duplicate clusters across 10,000 total candidates.
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Duplicate Cluster Count (pairwise IoU > 0.30)
- **Source Report**: `reports/nms/duplicate_characterization.md`

## Q2. Which IoU threshold produced the best trade-off?
- **Measured Value**: IoU Threshold `0.2` achieved the optimal trade-off with an F1 Score of `0.1938` (Metric A) and `0.0035` (Metric B), removing `7112` false positives while sacrificing only `17` true positives.
- **Dataset**: `ranked_by_combined_score.csv` & `ground_truth_symbols.json`
- **Metric**: F1 Score & False Positives Removed
- **Source Report**: `reports/nms/quantitative_results.md`

## Q3. Did NMS improve Top-10 localization?
- **Measured Value**: Top-10 MR Count went from `38` (Baseline) to `39` (NMS @ 0.2).
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Top-10 MR Count (Metric A)
- **Source Report**: `reports/nms/quantitative_results.md`

## Q4. Did NMS improve Top-50 localization?
- **Measured Value**: Top-50 MR Count went from `105` (Baseline) to `119` (NMS @ 0.2).
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Top-50 MR Count (Metric A)
- **Source Report**: `reports/nms/quantitative_results.md`

## Q5. Did NMS improve precision?
- **Measured Value**: Precision increased from `0.0347` (Baseline) to `0.1149` (NMS @ 0.2).
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Precision (Metric A)
- **Source Report**: `reports/nms/quantitative_results.md`

## Q6. Did NMS reduce recall?
- **Measured Value**: Recall went from `0.6486` (Baseline) to `0.6168` (NMS @ 0.2), representing a loss of `17` true positive symbols.
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Recall (Metric A) & True Positives Removed
- **Source Report**: `reports/nms/quantitative_results.md`

## Q7. Were remaining false positives predominantly duplicate detections?
- **Measured Value**: After NMS @ 0.2, duplicate detections accounted for `0` remaining false positives. Remaining errors are predominantly semantic structures such as `Accidental suppression of true symbols`.
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Failure Mode Counts
- **Source Report**: `reports/nms/failure_mode_analysis.md`

## Q8. Would NMS have prevented the architectural problems discovered in the structural discriminator experiments?
- **Verdict**: No. NMS is strictly a spatial de-duplication mechanism. It does not evaluate semantic validity or structural consistency. While NMS eliminates duplicate boxes around the same false positive, it cannot suppress isolated false positives like busbars, text, or conductor fragments. Structural discriminators remain essential for semantic filtering.
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Semantic False Positive Counts
- **Source Report**: `reports/nms/failure_mode_analysis.md`

## Q9. Does the evidence justify integrating NMS into the production pipeline?
- **Verdict**: Yes. NMS provides a massive `71.3%` reduction in redundant candidates and significantly improves Top-K ranking concentration and visual clarity with negligible `0.50s` computational overhead (`20053.2` candidates/sec throughput). Integrating NMS as a lightweight post-processing step immediately prior to expensive structural discriminators is highly justified.
- **Dataset**: `ranked_by_combined_score.csv`
- **Metric**: Suppression %, Runtime (s), and Cands/sec
- **Source Report**: `reports/nms/quantitative_results.md`
