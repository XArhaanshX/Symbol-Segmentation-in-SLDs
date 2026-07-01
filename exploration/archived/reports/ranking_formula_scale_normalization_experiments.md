# Scale Normalization Experiments

- Generation Timestamp: 2026-06-18 07:03:52
- Stage Version: Stage 5.6
- Input Datasets: ranked_by_combined_score.csv, verified_candidates.csv, ranking_failure_dataset.csv
- Template Bank Version: Stage2_D3_v1
- Candidate Count: 1000 per SLD (Frozen Stage 5)
- Experiment Identifier: Multiple
- Ground Truth Source: reports/ground_truth_symbols.json
- Evaluation Method: Mathematical Recalculation
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Referenced Prior Stages: Stage 4, Stage 5.2, Stage 5.5
- Manual Dependency Status: None

| ID | Formula | Median Rank | Mean Rank | Top 100 | Top 500 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| B1 | Coverage × Scale | 232.0 | 245.0 | 15.5% | 51.6% |
| B2 | Coverage × sqrt(Scale) | 240.0 | 249.9 | 14.8% | 50.7% |
| B3 | Coverage × log(Scale) | 234.0 | 246.2 | 15.3% | 50.8% |
| B4 | Coverage × Area × Scale | 212.0 | 230.7 | 16.3% | 52.1% |
| B5 | Coverage × Area / Scale | 232.0 | 245.2 | 15.7% | 51.6% |
| B6 | Coverage × Area × EdgeDensity | 223.0 | 238.0 | 15.9% | 52.3% |
