# Discriminator Redundancy Analysis

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

| Feature | Class | Best Correlation | Strongest Correlated Signal | Shared Variance (R2) |
| :--- | :--- | :---: | :--- | :---: |
| Stroke_Count | CLASS B (Partially Redundant) | -0.68 | chamfer_score | 45.8% |
| Branch_Point_Count | CLASS B (Partially Redundant) | -0.61 | chamfer_score | 37.0% |
| Endpoint_Count | CLASS B (Partially Redundant) | -0.62 | chamfer_score | 38.4% |
| Connected_Component_Count | CLASS B (Partially Redundant) | -0.64 | chamfer_score | 41.0% |
| Loop_Count | CLASS B (Partially Redundant) | -0.63 | chamfer_score | 40.2% |
| Hole_Count | CLASS B (Partially Redundant) | -0.55 | chamfer_score | 30.4% |
| Endpoint_Matching_Ratio | CLASS C (Redundant) | -0.72 | chamfer_score | 51.2% |
| Junction_Matching_Ratio | CLASS B (Partially Redundant) | -0.66 | chamfer_score | 43.0% |
| Average_Branch_Length | CLASS B (Partially Redundant) | 0.70 | chamfer_score | 48.9% |
| Maximum_Branch_Length | CLASS B (Partially Redundant) | 0.70 | chamfer_score | 48.9% |
| Contour_Hierarchy_Depth | CLASS B (Partially Redundant) | -0.56 | chamfer_score | 30.8% |
| Edge_Count_Difference | CLASS A (Novel) | -0.40 | chamfer_score | 16.1% |
| Junction_Similarity | CLASS A (Novel) | 0.09 | VerificationScore | 0.8% |
| Graph_Density_Difference | CLASS A (Novel) | 0.36 | chamfer_score | 13.3% |
| Graph_Edit_Distance_Approx | CLASS A (Novel) | -0.38 | chamfer_score | 14.7% |
| Largest_Component_Ratio | CLASS B (Partially Redundant) | 0.45 | chamfer_score | 20.5% |
| Degree_Distribution_Difference | CLASS A (Novel) | -0.21 | chamfer_score | 4.4% |
| Component_Area_Variance | CLASS A (Novel) | 0.36 | VerificationScore | 12.7% |
| Euler_Number | CLASS B (Partially Redundant) | -0.45 | chamfer_score | 20.0% |
| Node_Count_Difference | CLASS A (Novel) | -0.25 | VerificationScore | 6.1% |
| Endpoint_Similarity | CLASS A (Novel) | -0.19 | chamfer_score | 3.6% |
| Stroke_Density | CLASS A (Novel) | 0.25 | VerificationScore | 6.1% |
| Vertical_Stroke_Ratio | CLASS B (Partially Redundant) | -0.56 | template_width | 31.0% |
| Horizontal_Stroke_Ratio | CLASS B (Partially Redundant) | 0.59 | template_width | 35.1% |
| Branch_Length_Variance | CLASS A (Novel) | 0.00 |  | 0.0% |
