# Competitor Analysis

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

## Required Questions
1. **How far ahead is the competitor?** The top competitor is rank 1, while true symbols are rank >1000. Thousands of positions ahead.
2. **How many competitors outrank the symbol?** Equal to `symbol_rank - 1`.
3. **What score components create the advantage?** Detailed in Score Gap Analysis.
