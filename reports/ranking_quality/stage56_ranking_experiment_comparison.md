# Ranking Experiment Comparison Leaderboard

- Generation Timestamp: 2026-06-18 07:03:52
- Stage Version: Stage 5.6
- Input Datasets: ranked_by_combined_score.csv, verified_candidates.csv, ranking_failure_dataset.csv
- Template Bank Version: Stage2_D3_v1
- Candidate Count: 1000 per SLD (Frozen Stage 5)
- Experiment Identifier: All
- Ground Truth Source: reports/ground_truth_symbols.json
- Evaluation Method: Tiebreaker Sort
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Referenced Prior Stages: Stage 4, Stage 5.2, Stage 5.5
- Manual Dependency Status: None

| Rank | ID | Formula | Median Rank | Top 100 | Inversions Resolved |
| :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | B4 | Coverage × Area × Scale | 212.0 | 16.3% | 0 |
| 2 | A1 | Coverage × Area | 223.0 | 15.9% | 0 |
| 3 | B6 | Coverage × Area × EdgeDensity | 223.0 | 15.9% | 0 |
| 4 | C1 | 70% Verification + 30% Coverage | 223.0 | 15.9% | 0 |
| 5 | C2 | 80% Verification + 20% Coverage | 223.0 | 15.9% | 0 |
| 6 | C3 | 90% Verification + 10% Coverage | 223.0 | 15.9% | 0 |
| 7 | A2 | Coverage × sqrt(Area) | 232.0 | 15.7% | 0 |
| 8 | B5 | Coverage × Area / Scale | 232.0 | 15.7% | 0 |
| 9 | B1 | Coverage × Scale | 232.0 | 15.5% | 0 |
| 10 | B3 | Coverage × log(Scale) | 234.0 | 15.3% | 0 |
| 11 | A3 | Coverage × log(Area) | 239.0 | 14.4% | 0 |
| 12 | B2 | Coverage × sqrt(Scale) | 240.0 | 14.8% | 0 |
| 13 | A4 | Coverage × cbrt(Area) | 241.0 | 15.0% | 0 |
| 14 | A5 | Coverage only | 241.0 | 13.6% | 0 |
