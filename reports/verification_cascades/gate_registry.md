# Gate Registry

- Generation Timestamp: 2026-06-18 09:05:19
- Stage Version: Stage 5.10
- Input Datasets: verified_candidates.csv, ranked_by_combined_score.csv, topological_features_dataset.csv, stage59a_stroke_consistency_dataset.csv, stage59b_existence_features.csv, stage59b_discovery_dataset.csv
- Candidate Count: 0
- Ground Truth Source: ground_truth_symbols.json
- Association Radius: 25px
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Feature Source: Joined Metadata
- Experiment Identifier: N/A
- Gate Identifier: N/A
- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.8, Stage 5.9A, Stage 5.9B
- Manual Dependency Status: None

## Gate_ST_01
- Mathematical Definition: Stroke_Count <= Threshold
- Feature Source Dataset: topological
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_ST_02
- Mathematical Definition: Normalized_Stroke_Difference <= Threshold
- Feature Source Dataset: topological
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_CS_01
- Mathematical Definition: Stroke_Similarity >= Threshold
- Feature Source Dataset: consistency
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_CS_02
- Mathematical Definition: Stroke_Ratio <= Threshold
- Feature Source Dataset: consistency
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_EX_01
- Mathematical Definition: Contour_Perimeter >= Threshold
- Feature Source Dataset: existence
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_EX_02
- Mathematical Definition: Foreground_Pixel_Count >= Threshold
- Feature Source Dataset: existence
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_EX_03
- Mathematical Definition: Skeleton_Length >= Threshold
- Feature Source Dataset: existence
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_EX_04
- Mathematical Definition: Bounding_Box_Occupancy >= Threshold
- Feature Source Dataset: existence
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

## Gate_EX_05
- Mathematical Definition: Largest_Component_Ratio >= Threshold
- Feature Source Dataset: existence
- Target Failure Mode: Promoted Noise / FP
- Expected Retention Risk: Loss of small MR symbols
- Expected Rejection Behavior: Suppress out-of-distribution structural anomalies

