# Feature Separability Audit

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

### Average_Branch_Length
- MR vs Dominant FP: AUC=0.826, d=1.117, Overlap=24.7%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.626, d=0.362, Overlap=94.9%

### Branch_Length_Variance
- MR vs Dominant FP: AUC=0.500, d=0.000, Overlap=0.0%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.500, d=0.000, Overlap=0.0%

### Branch_Point_Count
- MR vs Dominant FP: AUC=0.899, d=1.897, Overlap=83.1%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.603, d=0.392, Overlap=71.3%

### Component_Area_Variance
- MR vs Dominant FP: AUC=0.737, d=0.767, Overlap=80.7%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.533, d=0.064, Overlap=79.1%

### Connected_Component_Count
- MR vs Dominant FP: AUC=0.882, d=1.842, Overlap=85.2%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.605, d=0.446, Overlap=96.2%

### Contour_Hierarchy_Depth
- MR vs Dominant FP: AUC=0.822, d=1.431, Overlap=75.0%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.609, d=0.416, Overlap=75.0%

### Degree_Distribution_Difference
- MR vs Dominant FP: AUC=0.746, d=1.040, Overlap=85.2%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.566, d=0.275, Overlap=67.2%

### Edge_Count_Difference
- MR vs Dominant FP: AUC=0.793, d=1.703, Overlap=70.7%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.584, d=0.376, Overlap=39.9%

### Endpoint_Count
- MR vs Dominant FP: AUC=0.885, d=1.860, Overlap=69.8%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.611, d=0.495, Overlap=84.2%

### Endpoint_Matching_Ratio
- MR vs Dominant FP: AUC=0.861, d=1.576, Overlap=76.9%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.589, d=0.415, Overlap=100.0%

### Endpoint_Similarity
- MR vs Dominant FP: AUC=0.675, d=0.169, Overlap=99.7%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.506, d=0.062, Overlap=99.5%

### Euler_Number
- MR vs Dominant FP: AUC=0.723, d=1.011, Overlap=83.3%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.570, d=0.335, Overlap=92.6%

### Graph_Density_Difference
- MR vs Dominant FP: AUC=0.780, d=0.856, Overlap=97.3%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.643, d=0.585, Overlap=98.8%

### Graph_Edit_Distance_Approx
- MR vs Dominant FP: AUC=0.780, d=1.680, Overlap=71.4%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.580, d=0.366, Overlap=40.6%

### Hole_Count
- MR vs Dominant FP: AUC=0.868, d=1.599, Overlap=100.0%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.615, d=0.331, Overlap=93.8%

### Horizontal_Stroke_Ratio
- MR vs Dominant FP: AUC=0.539, d=0.141, Overlap=90.9%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.523, d=0.081, Overlap=100.0%

### Junction_Matching_Ratio
- MR vs Dominant FP: AUC=0.850, d=1.555, Overlap=90.9%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.590, d=0.382, Overlap=100.0%

### Junction_Similarity
- MR vs Dominant FP: AUC=0.793, d=0.052, Overlap=66.6%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.584, d=0.080, Overlap=33.3%

### Largest_Component_Ratio
- MR vs Dominant FP: AUC=0.760, d=0.837, Overlap=84.6%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.567, d=0.281, Overlap=94.6%

### Loop_Count
- MR vs Dominant FP: AUC=0.877, d=1.800, Overlap=85.2%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.601, d=0.439, Overlap=96.2%

### Maximum_Branch_Length
- MR vs Dominant FP: AUC=0.826, d=1.117, Overlap=24.7%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.626, d=0.362, Overlap=94.9%

### Node_Count_Difference
- MR vs Dominant FP: AUC=0.675, d=0.864, Overlap=80.8%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.506, d=0.044, Overlap=67.7%

### Stroke_Count
- MR vs Dominant FP: AUC=0.951, d=2.647, Overlap=50.0%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.620, d=0.523, Overlap=83.3%

### Stroke_Density
- MR vs Dominant FP: AUC=0.647, d=0.503, Overlap=77.3%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.513, d=0.086, Overlap=50.2%

### Vertical_Stroke_Ratio
- MR vs Dominant FP: AUC=0.557, d=0.310, Overlap=100.0%
- MR vs Hard Negs: AUC=0.000, d=0.000, Overlap=100.0%
- MR vs Rand BG: AUC=0.540, d=0.167, Overlap=100.0%

