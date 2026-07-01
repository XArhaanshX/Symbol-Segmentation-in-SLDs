# Experiment Registry

- Generation Timestamp: 2026-06-18 07:53:34
- Stage Version: Stage 5.9
- Input Datasets: ranked_by_combined_score.csv, topological_features_dataset.csv, top100_competitor_sheet.csv
- Candidate Count: N/A
- Evaluation Method: Deterministic Mathematical Integration Validation
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Experiment Identifier: N/A
- Baseline Comparison ID: N/A
- Stroke Transformation Identifier: N/A
- Best Experiment Status: N/A
- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.2, Stage 5.5, Stage 5.6, Stage 5.8
- Manual Dependency Status: None

### Experiment BASE
- **Formula:** CombinedScore (Stage 5)
- **Stroke Integration:** NONE

### Experiment EXP_A
- **Formula:** Stroke Penalty Only
- **Stroke Integration:** T_EXP_01

### Experiment EXP_B
- **Formula:** CoverageAreaScore * Stroke Penalty
- **Stroke Integration:** T_EXP_01

### Experiment EXP_C
- **Formula:** VerificationScore * Stroke Penalty
- **Stroke Integration:** T_EXP_01

### Experiment EXP_D
- **Formula:** CombinedScore * Stroke Penalty
- **Stroke Integration:** T_EXP_01

