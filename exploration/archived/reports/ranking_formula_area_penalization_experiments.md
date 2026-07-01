# Area Penalization Experiments

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
| A1 | Coverage × Area | 223.0 | 238.0 | 15.9% | 52.3% |
| A2 | Coverage × sqrt(Area) | 232.0 | 245.1 | 15.7% | 51.6% |
| A3 | Coverage × log(Area) | 239.0 | 252.8 | 14.4% | 50.7% |
| A4 | Coverage × cbrt(Area) | 241.0 | 248.6 | 15.0% | 50.7% |
| A5 | Coverage only | 241.0 | 255.8 | 13.6% | 50.5% |
