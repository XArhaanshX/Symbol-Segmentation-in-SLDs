# Verification Weighting Experiments

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
| C1 | 70% Verification + 30% Coverage | 223.0 | 238.0 | 15.9% | 52.3% |
| C2 | 80% Verification + 20% Coverage | 223.0 | 238.0 | 15.9% | 52.3% |
| C3 | 90% Verification + 10% Coverage | 223.0 | 238.0 | 15.9% | 52.3% |
