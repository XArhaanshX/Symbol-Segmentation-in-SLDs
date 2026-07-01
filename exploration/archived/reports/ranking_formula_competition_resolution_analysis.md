# Competition Resolution Analysis

- Generation Timestamp: 2026-06-18 07:03:52
- Stage Version: Stage 5.6
- Input Datasets: ranked_by_combined_score.csv, verified_candidates.csv, ranking_failure_dataset.csv
- Template Bank Version: Stage2_D3_v1
- Candidate Count: 1000 per SLD (Frozen Stage 5)
- Experiment Identifier: All
- Ground Truth Source: reports/ground_truth_symbols.json
- Evaluation Method: Inversion Tracking
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Referenced Prior Stages: Stage 4, Stage 5.2, Stage 5.5
- Manual Dependency Status: None

| ID | Formula | Resolved | Unchanged | Worsened |
| :--- | :--- | :---: | :---: | :---: |
| A1 | Coverage × Area | 0 | 0 | 0 |
| A2 | Coverage × sqrt(Area) | 0 | 0 | 0 |
| A3 | Coverage × log(Area) | 0 | 0 | 0 |
| A4 | Coverage × cbrt(Area) | 0 | 0 | 0 |
| A5 | Coverage only | 0 | 0 | 0 |
| B1 | Coverage × Scale | 0 | 0 | 0 |
| B2 | Coverage × sqrt(Scale) | 0 | 0 | 0 |
| B3 | Coverage × log(Scale) | 0 | 0 | 0 |
| B4 | Coverage × Area × Scale | 0 | 0 | 0 |
| B5 | Coverage × Area / Scale | 0 | 0 | 0 |
| B6 | Coverage × Area × EdgeDensity | 0 | 0 | 0 |
| C1 | 70% Verification + 30% Coverage | 0 | 0 | 0 |
| C2 | 80% Verification + 20% Coverage | 0 | 0 | 0 |
| C3 | 90% Verification + 10% Coverage | 0 | 0 | 0 |
