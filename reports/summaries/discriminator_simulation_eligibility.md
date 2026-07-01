# Simulation Eligibility Report

- Generation Timestamp: 2026-06-18 07:35:59
- Stage Version: Stage 5.8
- Input Datasets: ranked_by_combined_score.csv, top100_competitor_sheet.csv, ground_truth_symbols.json
- Template Bank Version: Stage2_D3_v1
- Ground Truth Source: reports/ground_truth_symbols.json
- Evaluation Method: N/A
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Referenced Prior Stages: Stage 4, Stage 5.2, Stage 5.5, Stage 5.6
- Manual Dependency Status: Competitor Family Classification from 5.5 (if available)

### Stroke_Count -> ELIGIBLE
### Branch_Point_Count -> EXCLUDED
- Overlap > 50% (83.1%)
### Endpoint_Count -> EXCLUDED
- Overlap > 50% (69.8%)
### Connected_Component_Count -> EXCLUDED
- Overlap > 50% (85.2%)
### Loop_Count -> EXCLUDED
- Overlap > 50% (85.2%)
### Hole_Count -> EXCLUDED
- Overlap > 50% (100.0%)
### Endpoint_Matching_Ratio -> EXCLUDED
- Overlap > 50% (76.9%)
- Redundant Signal (r2=0.51 w/ chamfer_score)
### Junction_Matching_Ratio -> EXCLUDED
- Overlap > 50% (90.9%)
### Average_Branch_Length -> ELIGIBLE
### Maximum_Branch_Length -> ELIGIBLE
### Contour_Hierarchy_Depth -> EXCLUDED
- Overlap > 50% (75.0%)
### Edge_Count_Difference -> EXCLUDED
- Overlap > 50% (70.7%)
### Junction_Similarity -> EXCLUDED
- d < 0.80 (0.05)
- Overlap > 50% (66.6%)
### Graph_Density_Difference -> EXCLUDED
- Overlap > 50% (97.3%)
### Graph_Edit_Distance_Approx -> EXCLUDED
- Overlap > 50% (71.4%)
### Largest_Component_Ratio -> EXCLUDED
- Overlap > 50% (84.6%)
### Degree_Distribution_Difference -> EXCLUDED
- AUC < 0.75 (0.75)
- Overlap > 50% (85.2%)
### Component_Area_Variance -> EXCLUDED
- AUC < 0.75 (0.74)
- d < 0.80 (0.77)
- Overlap > 50% (80.7%)
### Euler_Number -> EXCLUDED
- AUC < 0.75 (0.72)
- Overlap > 50% (83.3%)
### Node_Count_Difference -> EXCLUDED
- AUC < 0.75 (0.68)
- Overlap > 50% (80.8%)
### Endpoint_Similarity -> EXCLUDED
- AUC < 0.75 (0.68)
- d < 0.80 (0.17)
- Overlap > 50% (99.7%)
### Stroke_Density -> EXCLUDED
- AUC < 0.75 (0.65)
- d < 0.80 (0.50)
- Overlap > 50% (77.3%)
### Vertical_Stroke_Ratio -> EXCLUDED
- AUC < 0.75 (0.56)
- d < 0.80 (0.31)
- Overlap > 50% (100.0%)
### Horizontal_Stroke_Ratio -> EXCLUDED
- AUC < 0.75 (0.54)
- d < 0.80 (0.14)
- Overlap > 50% (90.9%)
### Branch_Length_Variance -> EXCLUDED
- AUC < 0.75 (0.50)
- d < 0.80 (0.00)
