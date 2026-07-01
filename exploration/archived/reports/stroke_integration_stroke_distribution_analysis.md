# Stroke Count Distribution Validation

- Generation Timestamp: 2026-06-18 07:53:34
- Stage Version: Stage 5.9
- Input Datasets: ranked_by_combined_score.csv, topological_features_dataset.csv, top100_competitor_sheet.csv
- Candidate Count: 10000
- Evaluation Method: Deterministic Mathematical Integration Validation
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Experiment Identifier: N/A
- Baseline Comparison ID: N/A
- Stroke Transformation Identifier: N/A
- Best Experiment Status: N/A
- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.2, Stage 5.5, Stage 5.6, Stage 5.8
- Manual Dependency Status: None

| Group | Min | Max | Mean | Median | StdDev | P90 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| True MR | 2.0 | 22.0 | 6.00 | 4.00 | 4.36 | 13.00 |
| Dominant FP | 5.0 | 39.0 | 18.97 | 19.00 | 6.25 | 26.50 |
| Hard Negative | 0 | 0 | 0.00 | 0.00 | 0.00 | 0.00 |
| Random BG | 2.0 | 26.0 | 8.89 | 8.00 | 6.20 | 18.00 |
