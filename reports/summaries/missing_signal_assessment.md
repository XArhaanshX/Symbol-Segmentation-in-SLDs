# Missing Signal Assessment

- Generation Timestamp: 2026-06-17 13:20:31
- Stage Version: Stage 5.5
- Input Files: ranked_by_combined_score.csv, scale_vs_performance_dataset.csv, ground_truth_symbols.json
- Ground Truth Source: reports/ground_truth_symbols.json
- Association Radius: 25px
- Template Bank Version: Stage2_D3_v1
- Manifest Version: outputs/template_bank/template_bank_manifest.csv
- Dataset Size: 264852 candidates
- Analysis Method: Evidence-driven diagnostic audit

**Manual Review Dependency Status**: Manual classification not completed — dominance statistics unavailable.

Evaluated Hypotheses based on generated datasets:
- **Scale-awareness deficiency**: Supported. Mean Scale Ratio of competitors is > 1.0 (from `competitor_scale_analysis.md`).
- **Geometry discrimination deficiency**: Supported. High coverage deltas (from `score_gap_analysis.md`) suggest basic geometry is insufficient.
- **Verification weighting deficiency**: Inconclusive until dominance statistics complete.
