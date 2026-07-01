# Per-Scale Competition Study

- Generation Timestamp: 2026-06-18 07:03:52
- Stage Version: Stage 5.6
- Input Datasets: ranked_by_combined_score.csv, verified_candidates.csv, ranking_failure_dataset.csv
- Template Bank Version: Stage2_D3_v1
- Candidate Count: 1000 per SLD (Frozen Stage 5)
- Experiment Identifier: Baseline
- Ground Truth Source: reports/ground_truth_symbols.json
- Evaluation Method: Scale Stratification
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Referenced Prior Stages: Stage 4, Stage 5.2, Stage 5.5
- Manual Dependency Status: None

| Regime | Count | Median Rank | Mean Rank |
| :--- | :---: | :---: | :---: |
| A | 296 | 198.5 | 302.7 |
| B | 1 | 580.0 | 580.0 |
