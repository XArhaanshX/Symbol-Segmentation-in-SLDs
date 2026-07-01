# Formal Stage 6 Readiness Gate

- Generation Timestamp: 2026-06-18 09:05:21
- Stage Version: Stage 5.10
- Input Datasets: verified_candidates.csv, ranked_by_combined_score.csv, topological_features_dataset.csv, stage59a_stroke_consistency_dataset.csv, stage59b_existence_features.csv, stage59b_discovery_dataset.csv
- Candidate Count: 0
- Ground Truth Source: ground_truth_symbols.json
- Association Radius: 25px
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Feature Source: Joined Metadata
- Experiment Identifier: N/A
- Gate Identifier: N/A
- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.8, Stage 5.9A, Stage 5.9B
- Manual Dependency Status: None

- Criterion A (MR >= 95%): PASS (96.3%)
- Criterion B (Reg D >= 90%): PASS (100.0%)
- Criterion C (Noise >= 80%): FAIL (0.0%)
- Criterion D (FP >= 80%): FAIL (73.7%)
- Criterion L (Viable gate exists): PASS
- Q1. Increased MR Density?: YES (Gain: 13.92x)
- Q2. Deterministic Utility Selection?: YES (reports/stage510_threshold_utility_ranking.md)

## VERDICT: NOT READY FOR STAGE 6 (Criteria failed)
