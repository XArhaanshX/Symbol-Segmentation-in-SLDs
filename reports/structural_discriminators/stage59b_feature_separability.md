# Feature Separability Audit

- Generation Timestamp: 2026-06-18 08:39:27
- Stage Version: Stage 5.9B
- Input Datasets: ranked_by_combined_score.csv, topological_features_dataset.csv, template_bank_manifest.csv
- Evaluation Method: Separability
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.2, Stage 5.5, Stage 5.8, Stage 5.9, Stage 5.9A
- Manual Dependency Status: None

| Feature | AUC (vs GrpE) | AUC (vs GrpD) | AUC (vs GrpB) |
| :--- | :---: | :---: | :---: |
| Foreground_Pixel_Count | 0.837 | 0.000 | 0.954 |
| Foreground_Pixel_Ratio | 0.744 | 0.000 | 0.884 |
| Foreground_Bounding_Box_Fill | 0.782 | 0.000 | 0.591 |
| Bounding_Box_Occupancy | 0.782 | 0.000 | 0.764 |
| Convex_Hull_Occupancy | 0.786 | 0.000 | 0.507 |
| Connected_Component_Count | 0.772 | 0.000 | 0.884 |
| Largest_Component_Area | 0.744 | 0.000 | 0.800 |
| Largest_Component_Ratio | 0.666 | 0.000 | 0.761 |
| Component_Area_Variance | 0.814 | 0.000 | 0.736 |
| Skeleton_Length | 0.834 | 0.000 | 0.954 |
| Average_Segment_Length | 0.649 | 0.000 | 0.833 |
| Maximum_Segment_Length | 0.649 | 0.000 | 0.833 |
| Skeleton_Density | 0.783 | 0.000 | 0.565 |
| Contour_Area | 0.796 | 0.000 | 0.913 |
| Contour_Perimeter | 0.841 | 0.000 | 0.957 |
| Contour_Compactness | 0.685 | 0.000 | 0.823 |
| Contour_Fill_Ratio | 0.777 | 0.000 | 0.881 |
| Edge_Pixel_Count | 0.774 | 0.000 | 0.944 |
| Edge_Density | 0.811 | 0.000 | 0.551 |
| Foreground_Ratio | 0.798 | 0.000 | 0.932 |
| Skeleton_Length_Ratio | 0.778 | 0.000 | 0.903 |
| Contour_Area_Ratio | 0.796 | 0.000 | 0.844 |
| Occupancy_Ratio | 0.778 | 0.000 | 0.741 |
| Convex_Hull_Occupancy_Ratio | 0.754 | 0.000 | 0.570 |
