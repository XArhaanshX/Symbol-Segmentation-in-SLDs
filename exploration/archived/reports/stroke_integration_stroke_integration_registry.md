# Stroke Integration Registry

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

### Transformation T_INV_01
- **Formula:** `1.0 / (1.0 + 0.1 * Stroke_Count)`
- **Expected Behavioral Effect:** Rapid decay for complex objects. Stroke 0=1.0, Stroke 20=0.33.
- **Monotonicity:** Strictly Decreasing.

### Transformation T_EXP_01
- **Formula:** `exp(-0.05 * Stroke_Count)`
- **Expected Behavioral Effect:** Exponential decay. Stroke 0=1.0, Stroke 20=0.36.
- **Monotonicity:** Strictly Decreasing.
