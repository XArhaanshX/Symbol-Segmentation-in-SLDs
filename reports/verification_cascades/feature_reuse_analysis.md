# Feature Reuse Analysis

- Generation Timestamp: 2026-06-18 09:05:21
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

## Stroke_Count
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Normalized_Stroke_Difference
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Stroke_Similarity
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Stroke_Ratio
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Contour_Perimeter
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Foreground_Pixel_Count
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Skeleton_Length
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Bounding_Box_Occupancy
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

## Largest_Component_Ratio
- Class: REUSED (Topological) if pre-existing, NEW_COMPUTATION_REQUIRED otherwise.

