# Structural Discriminator Leaderboard

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

| Rank | Feature | AUC (vs DomFP) | Cohen's d (vs DomFP) | Overlap (vs DomFP) | AUC (vs HardNeg) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | Stroke_Count | 0.951 | 2.647 | 50.0% | 0.000 |
| 2 | Branch_Point_Count | 0.899 | 1.897 | 83.1% | 0.000 |
| 3 | Endpoint_Count | 0.885 | 1.860 | 69.8% | 0.000 |
| 4 | Connected_Component_Count | 0.882 | 1.842 | 85.2% | 0.000 |
| 5 | Loop_Count | 0.877 | 1.800 | 85.2% | 0.000 |
| 6 | Hole_Count | 0.868 | 1.599 | 100.0% | 0.000 |
| 7 | Endpoint_Matching_Ratio | 0.861 | 1.576 | 76.9% | 0.000 |
| 8 | Junction_Matching_Ratio | 0.850 | 1.555 | 90.9% | 0.000 |
| 9 | Average_Branch_Length | 0.826 | 1.117 | 24.7% | 0.000 |
| 10 | Maximum_Branch_Length | 0.826 | 1.117 | 24.7% | 0.000 |
| 11 | Contour_Hierarchy_Depth | 0.822 | 1.431 | 75.0% | 0.000 |
| 12 | Edge_Count_Difference | 0.793 | 1.703 | 70.7% | 0.000 |
| 13 | Junction_Similarity | 0.793 | 0.052 | 66.6% | 0.000 |
| 14 | Graph_Density_Difference | 0.780 | 0.856 | 97.3% | 0.000 |
| 15 | Graph_Edit_Distance_Approx | 0.780 | 1.680 | 71.4% | 0.000 |
| 16 | Largest_Component_Ratio | 0.760 | 0.837 | 84.6% | 0.000 |
| 17 | Degree_Distribution_Difference | 0.746 | 1.040 | 85.2% | 0.000 |
| 18 | Component_Area_Variance | 0.737 | 0.767 | 80.7% | 0.000 |
| 19 | Euler_Number | 0.723 | 1.011 | 83.3% | 0.000 |
| 20 | Node_Count_Difference | 0.675 | 0.864 | 80.8% | 0.000 |
| 21 | Endpoint_Similarity | 0.675 | 0.169 | 99.7% | 0.000 |
| 22 | Stroke_Density | 0.647 | 0.503 | 77.3% | 0.000 |
| 23 | Vertical_Stroke_Ratio | 0.557 | 0.310 | 100.0% | 0.000 |
| 24 | Horizontal_Stroke_Ratio | 0.539 | 0.141 | 90.9% | 0.000 |
| 25 | Branch_Length_Variance | 0.500 | 0.000 | 0.0% | 0.000 |
