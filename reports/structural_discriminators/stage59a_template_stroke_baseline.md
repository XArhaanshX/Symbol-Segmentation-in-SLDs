# Template Stroke Baseline

- Generation Timestamp: 2026-06-18 08:13:35
- Stage Version: Stage 5.9A
- Input Datasets: ranked_by_combined_score.csv, topological_features_dataset.csv, template_bank_manifest.csv
- Candidate Count: N/A
- Evaluation Method: Deterministic Mathematical Integration Validation
- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)
- Association Radius: 25px
- Experiment Identifier: N/A
- Baseline Comparison ID: BASE
- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.2, Stage 5.5, Stage 5.8, Stage 5.9
- Manual Dependency Status: None

### Methodology Requirement Check
PASS: Template Stroke_Count was extracted using the exact same `extract_topological_features` method from Stage 5.8 to guarantee 1:1 comparability.

### Distribution
- Min: 3.0
- Max: 10.0
- Mean: 5.45
- Median: 5.0
